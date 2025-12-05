import json
import traceback
import uuid
from operator import truediv

from decouple import config
from django.contrib.auth.models import User
from google import genai

from company.models import Company, Announcement
from dashboard.models import Task, InsightSuggestion
from message.models import Conversation
from projects.models import Project
from teams.models import Team

# TODO MESSAGE/EMAIL INTEGRATION

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_KEY = config("GEMINI_API_KEY", default="AIzaSyCxNumlNs-xAtdbys5j0a2f9OXa2q8Ayrs")
client = genai.Client(api_key=GEMINI_API_KEY)


def _gather_user_context(user):
    companies = Company.objects.filter(
        memberships__user=user
    ).distinct()

    teams = Team.objects.filter(
        memberships__user=user
    ).distinct()

    projects = (
        Project.objects.filter(collaborators=user) |
        Project.objects.filter(lead=user)
    ).distinct()

    tasks = (
        Task.objects.filter(users=user).order_by("-pub_date")
    )

    announcements = (
        Announcement.objects.filter(company__in=companies)
        .order_by("-created_at")
    )

    conversations = (
        Conversation.objects.filter(participants=user)
    )

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
        "companies": [
            {
                "id": company.id,
                "name": company.name,
                "email": company.email,
                "phone": company.phone,
                "location": company.location,
                "description": company.description,
                "website": company.website,
                "members": [
                    {
                        "id": membership.user.id,
                        "username": membership.user.username,
                        "email": membership.user.email,
                        "role": membership.role,
                    }
                    for membership in company.memberships.all()
                ]
            }
            for company in companies
        ],
        "team": [
            {
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "members": [
                    {
                        "id": membership.user.id,
                        "username": membership.user.username,
                        "email": membership.user.email,
                        "role": membership.role
                    }
                    for membership in team.memberships.all()
                ]
            }
            for team in teams
        ],
        "project": [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "lead": {
                    "id": project.lead.id,
                    "username": project.lead.username,
                    "email": project.lead.email,
                },
                "collaborators": [
                    {
                        "id": collaborator.id,
                        "username": collaborator.username,
                        "email": collaborator.email,
                    }
                    for collaborator in project.collaborators.all()
                ],
                "companies": [company.id for company in project.companies.all()],
                "team": project.team.id if project.team else None,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            }
            for project in projects
        ],
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "content": task.content,
                "status": task.status,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "pub_date": task.pub_date.isoformat(),
                "team": task.team.id if task.team else None,
                "project": task.project.id if task.project else None,
            }
            for task in tasks
        ],
        "announcements": [
            {
                "id": announcement.id,
                "company_id": announcement.company.id,
                "title": announcement.title,
                "content": announcement.content,
                "created_at": announcement.created_at.isoformat(),
                "updated_at": announcement.updated_at.isoformat(),
                "tasks": [task.id for task in announcement.tasks.all()]
            }
            for announcement in announcements
        ],
        "conversations": [
            {
                "id": conversation.id,
                "title": conversation.title,
                "participants": [
                    {
                        "id": participant.id,
                        "username": participant.username,
                        "email": participant.email,
                    }
                    for participant in conversation.participants.all()
                ],
                "team": conversation.team.id if conversation.team else None,
                "messages": [
                    {
                        "id": message.id,
                        "sender": {
                            "id": message.sender.id,
                            "username": message.sender.username,
                            "email": message.sender.email,
                        },
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                    }
                    for message in conversation.messages.all().order_by("-timestamp")[:1]
                ]
            }
            for conversation in conversations
        ]
    }


def _build_prompt(ctx):
    return (
        "You are Orbit, a CRM productivity assistant.\n\n"
        "You receive CRM context as JSON in the `context` field below. "
        "Using that context, propose high-quality actionable suggestions for the user.\n\n"
        "Rules:\n"
        "(1) Output **valid JSON only**. Do not include '```json' preceding the JSON content or '```' succeeding it. "
        "Do not output a Python list.\n"
        "(2) No commentary.\n"
        "(3) JSON schema:\n"
        "{\n"
        '  "suggestions": [\n'
        "    {\n"
        '      "type": "create_task" | "create_event" | "create_announcement" | '
        '"send_message" | "send_email" | "general_insight",\n'
        "      // if type == create_task\n"
        '      "title": string,\n'
        '      "content": string, // Include source and context\n'
        '      "deadline": "YYYY-MM-DD" | null,\n'
        '      "project_or_team_id": integer | null, // If task is applicable to either team or project \n'
        '      "users"; [integer], // User IDs assigned to task, as allowed by current user\'s permissions\n'
        "      // if type == create_event\n"
        '      "title": string,\n'
        '      "content": string, // Include source and context\n'
        '      "start_datetime": "YYYY-MM-DD HH:MM:SS",\n'
        '      "end_datetime": "YYYY-MM-DD HH:MM:SS",\n\n'
        '      "project_or_team_id": integer | null, // If event is applicable to either team or project \n'
        '      "users": [integer], // User IDs involved in event, as allowed by current user\'s permissions\n'
        "      // if type == create_announcement "
        "(Note: Only administrators or owners of companies can create announcements\n"
        '      "title": string,\n'
        '      "content": string, // Include source and context\n'
        '      "company_id": integer,\n'
        '      "tasks": [integer], // Related task IDs\n'
        "      // if type == send_message\n"
        '      "conversation_id": integer\n,'
        '      "content": string, // Include source and context\n'
        '      "team_id": integer | null, // If message is in thread with team\n'
        "      // if type == send_email\n"
        '      "recipient_user_ids": [integer],\n'
        '      "subject": string,\n'
        '      "content": string, // Include source and context\n'
        "      // if type == general_insight\n"
        '      "content": string // Include source and context\n'
        "    }\n"
        "  ],\n"
        '  "fallback": boolean // true if there is not enough context or there are no suggestions\n'
        "}\n\n"
        "(4) If there is not enough context or no good suggestions, use the fallback field set to true.\n"
        "The context is as follows: `context`=\n"
        "(5) The `content` in each suggestion should follow with what the suggestion should accomplish. For example, "
        "the `content` in a message suggestion should be addressed to recipient, rather than a description of the "
        "message suggestion itself.\n"
        f"{json.dumps(ctx, ensure_ascii=False)}\n"
    )


def generate_orbit_insights(user, persist=True):
    ctx = _gather_user_context(user)
    prompt = _build_prompt(ctx)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        raw_text = response.text or ""
        json_declaration_start_index = raw_text.find("```json")
        if json_declaration_start_index != -1:
            raw_text = raw_text[json_declaration_start_index + len("```json"):raw_text.rfind("```")]
        print(raw_text)
        data = json.loads(raw_text)

        suggestions = data.get("suggestions") or []
        fallback = bool(data.get("fallback"))

        if not isinstance(suggestions, list):
            suggestions = []
            fallback = True

        batch_id = uuid.uuid4().hex if persist else None
        created = []

        if persist:
            for suggestion in suggestions:
                type = suggestion.get("type") or "general_insight"
                created.append(
                    InsightSuggestion.objects.create(
                        user=user,
                        suggestion_type=type,
                        raw_data=suggestion,
                        batch_id=batch_id
                    )
                )

        return {
            "suggestions": suggestions,
            "fallback": fallback,
            "batch_id": batch_id,
            "created": created
        }
    except Exception as e:
        print("Orbit insights error:", e)
        traceback.print_exc()
        return {
            "suggestions": [],
            "fallback": True,
            "batch_id": None,
            "created": []
        }


def test():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Write an email to a customer updating them on our updated shipment."
    )

    response2 = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=["Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"]
    )

    # Task.objects.create(
    #     name="Email Update",
    #     description=response.choices[0].message["content"],
    #     status="in_progress",
    #     assigned_to="user123"
    # )

    print(response.text)

    for part in response2.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save("../media/generated_test_image.png")
