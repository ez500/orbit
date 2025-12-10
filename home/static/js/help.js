/**
 * VerAlign Help System
 * Simple modal-based help for UI elements
 */

(function initHelpSystem() {
    'use strict';

    // Help content for different pages
    const helpContent = {
        'dashboard': {
            title: 'Dashboard Help',
            icon: 'fa-dashboard',
            sections: [
                {
                    title: 'Overview',
                    icon: 'fa-info-circle',
                    description: 'The Dashboard is your command center for managing all aspects of VerAlign.',
                    items: []
                },
                {
                    title: 'Key Features',
                    icon: 'fa-star',
                    description: 'Here are the main features available on the Dashboard:',
                    items: [
                        {
                            title: 'Quick Stats',
                            description: 'View important metrics and KPIs at a glance, including active projects, pending tasks, and team activity.'
                        },
                        {
                            title: 'Recent Activity',
                            description: 'See the latest updates from your projects, tasks, and team members in real-time.'
                        },
                        {
                            title: 'Quick Actions',
                            description: 'Access frequently used actions like creating new projects, tasks, or starting conversations.'
                        },
                        {
                            title: 'Notifications',
                            description: 'Stay updated with important alerts, mentions, and reminders.'
                        }
                    ]
                },
                {
                    title: 'Navigation Tips',
                    icon: 'fa-compass',
                    description: 'Use the sidebar to navigate between different sections:',
                    items: [
                        {
                            title: 'Sidebar Navigation',
                            description: 'Click any menu item in the sidebar to navigate to that section. Use the collapse button to maximize your workspace.'
                        },
                        {
                            title: 'Search',
                            description: 'Use the search bar at the top of the sidebar to quickly find projects, tasks, or team members.'
                        }
                    ]
                }
            ]
        },
        'messages': {
            title: 'Messages Help',
            icon: 'fa-comments',
            sections: [
                {
                    title: 'Messaging Overview',
                    icon: 'fa-info-circle',
                    description: 'Stay connected with your team through direct messages and group conversations.',
                    items: []
                },
                {
                    title: 'Features',
                    icon: 'fa-star',
                    description: 'Available messaging features:',
                    items: [
                        {
                            title: 'Direct Messages',
                            description: 'Send one-on-one messages to team members. Click on a user to start a conversation.'
                        },
                        {
                            title: 'Team Conversations',
                            description: 'Create group chats for teams or projects. Add multiple participants to collaborate together.'
                        },
                        {
                            title: 'File Attachments',
                            description: 'Share images, PDFs, and other files directly in your conversations.'
                        },
                        {
                            title: 'Message Threading',
                            description: 'Reply to specific messages to create organized threads and keep conversations focused.'
                        },
                        {
                            title: 'Edit & Delete',
                            description: 'Hover over your messages to edit or delete them. Changes are reflected in real-time.'
                        },
                        {
                            title: 'Live Updates',
                            description: 'Messages update automatically - no need to refresh the page to see new messages.'
                        }
                    ]
                }
            ]
        },
        'projects': {
            title: 'Projects Help',
            icon: 'fa-folder-open',
            sections: [
                {
                    title: 'Project Management',
                    icon: 'fa-info-circle',
                    description: 'Organize and track your projects from start to finish.',
                    items: []
                },
                {
                    title: 'Features',
                    icon: 'fa-star',
                    description: 'Project management features:',
                    items: [
                        {
                            title: 'Create Projects',
                            description: 'Create new projects with descriptions, deadlines, and team assignments.'
                        },
                        {
                            title: 'Track Progress',
                            description: 'Monitor project status, milestones, and completion percentage.'
                        },
                        {
                            title: 'Collaborate',
                            description: 'Assign team members, share documents, and communicate within project context.'
                        }
                    ]
                }
            ]
        },
        'tasks': {
            title: 'Tasks Help',
            icon: 'fa-tasks',
            sections: [
                {
                    title: 'Task Management',
                    icon: 'fa-info-circle',
                    description: 'Stay organized with comprehensive task tracking.',
                    items: []
                },
                {
                    title: 'Features',
                    icon: 'fa-star',
                    description: 'Task management features:',
                    items: [
                        {
                            title: 'Create Tasks',
                            description: 'Create tasks with titles, descriptions, due dates, and priority levels.'
                        },
                        {
                            title: 'Assign Tasks',
                            description: 'Assign tasks to team members and track their progress.'
                        },
                        {
                            title: 'Track Status',
                            description: 'Monitor task completion, overdue items, and upcoming deadlines.'
                        }
                    ]
                }
            ]
        },
        'teams': {
            title: 'Teams Help',
            icon: 'fa-users',
            sections: [
                {
                    title: 'Team Collaboration',
                    icon: 'fa-info-circle',
                    description: 'Manage your teams and collaborate effectively.',
                    items: []
                },
                {
                    title: 'Features',
                    icon: 'fa-star',
                    description: 'Team management features:',
                    items: [
                        {
                            title: 'Team Members',
                            description: 'View and manage team members, their roles, and permissions.'
                        },
                        {
                            title: 'Team Chat',
                            description: 'Create team-specific conversations for better communication.'
                        },
                        {
                            title: 'Shared Resources',
                            description: 'Access shared files, documents, and resources within your team.'
                        }
                    ]
                }
            ]
        },
        'profile': {
            title: 'Profile Help',
            icon: 'fa-user',
            sections: [
                {
                    title: 'Profile Settings',
                    icon: 'fa-info-circle',
                    description: 'Customize your profile and account settings.',
                    items: []
                },
                {
                    title: 'Customization',
                    icon: 'fa-star',
                    description: 'Available customization options:',
                    items: [
                        {
                            title: 'Theme Settings',
                            description: 'Choose your preferred color theme (light/dark) and accent colors.'
                        },
                        {
                            title: 'Accessibility',
                            description: 'Adjust font sizes, spacing, and enable high contrast mode for better readability.'
                        },
                        {
                            title: 'Profile Information',
                            description: 'Update your name, bio, timezone, and profile picture.'
                        },
                        {
                            title: 'Sidebar Customization',
                            description: 'Enable edit mode to reorder navigation items and hide unused features.'
                        }
                    ]
                }
            ]
        }
    };

    // Determine current page
    function getCurrentPage() {
        const path = window.location.pathname;

        if (path.includes('/dashboard')) return 'dashboard';
        if (path.includes('/message')) return 'messages';
        if (path.includes('/projects')) return 'projects';
        if (path.includes('/tasks')) return 'tasks';
        if (path.includes('/teams')) return 'teams';
        if (path.includes('/accounts/') || path.includes('/profile')) return 'profile';

        // Default to dashboard help
        return 'dashboard';
    }

    // Create help modal HTML
    function createHelpModal() {
        const currentPage = getCurrentPage();
        const content = helpContent[currentPage] || helpContent['dashboard'];

        let sectionsHTML = '';
        content.sections.forEach(section => {
            let itemsHTML = '';

            if (section.items.length > 0) {
                itemsHTML = '<ul class="help-items">';
                section.items.forEach(item => {
                    itemsHTML += `
                        <li class="help-item">
                            <div class="help-item-title">${item.title}</div>
                            <div class="help-item-description">${item.description}</div>
                        </li>
                    `;
                });
                itemsHTML += '</ul>';
            }

            sectionsHTML += `
                <div class="help-section">
                    <h3 class="help-section-title">
                        <i class="fas ${section.icon}"></i>
                        ${section.title}
                    </h3>
                    ${section.description ? `<p class="help-section-description">${section.description}</p>` : ''}
                    ${itemsHTML}
                </div>
            `;
        });

        return `
            <div class="help-modal-overlay" id="helpModalOverlay">
                <div class="help-modal">
                    <div class="help-modal-header">
                        <h2 class="help-modal-title">
                            <i class="fas ${content.icon}"></i>
                            ${content.title}
                        </h2>
                        <button class="help-modal-close" id="helpModalClose" aria-label="Close help">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="help-modal-body">
                        ${sectionsHTML}
                    </div>
                </div>
            </div>
        `;
    }

    // Initialize help system
    function init() {
        // Only show help on authenticated pages
        if (!document.querySelector('.sidebar')) {
            console.log('[Help] Not showing on non-authenticated page');
            return;
        }

        // Create help button
        const helpButton = document.createElement('button');
        helpButton.className = 'help-icon-btn';
        helpButton.setAttribute('aria-label', 'Help');
        helpButton.innerHTML = '<i class="fas fa-question"></i>';
        document.body.appendChild(helpButton);

        // Create modal (initially hidden)
        const modalHTML = createHelpModal();
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer.firstElementChild);

        const overlay = document.getElementById('helpModalOverlay');
        const closeBtn = document.getElementById('helpModalClose');

        // Show modal
        helpButton.addEventListener('click', () => {
            overlay.classList.add('show');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        });

        // Close modal
        function closeModal() {
            overlay.classList.remove('show');
            document.body.style.overflow = ''; // Restore scrolling
        }

        closeBtn.addEventListener('click', closeModal);

        // Close when clicking outside modal
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && overlay.classList.contains('show')) {
                closeModal();
            }
        });

        console.log('[Help] Help system initialized for page:', getCurrentPage());
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
