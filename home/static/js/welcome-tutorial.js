/**
 * VerAlign Welcome Tutorial
 * Guides new users through the interface
 */

(function initWelcomeTutorial() {
    'use strict';

    // Define the tutorial steps
    const tutorialSteps = [
        {
            target: '.sidebar',
            title: 'Welcome to VerAlign!',
            content: 'Let\'s take a quick tour of the interface. This is your navigation sidebar where you can access all key features.'
        },
        {
            target: '[data-nav-id="dashboard"]',
            title: 'Dashboard',
            content: 'The Dashboard is your command center. View key metrics, recent activity, and important insights at a glance.'
        },
        {
            target: '[data-nav-id="projects"]',
            title: 'Projects',
            content: 'Manage all your projects here. Create new projects, track progress, and collaborate with your team.'
        },
        {
            target: '[data-nav-id="tasks"]',
            title: 'Tasks',
            content: 'Stay organized with the task manager. Create, assign, and track tasks across all your projects.'
        },
        {
            target: '[data-nav-id="teams"]',
            title: 'Teams',
            content: 'Collaborate with your teams. Manage team members, share resources, and communicate effectively.'
        },
        {
            target: '.search-wrapper',
            title: 'Quick Search',
            content: 'Use the search bar to quickly find projects, tasks, or team members across the platform.'
        },
        {
            target: '.toggle-btn',
            title: 'Collapse Sidebar',
            content: 'Need more space? Click this button to collapse the sidebar and expand your workspace.',
            onShow: function(element) {
                // Ensure sidebar is expanded for this step
                const sidebar = document.querySelector('.sidebar');
                if (sidebar && sidebar.classList.contains('collapsed')) {
                    sidebar.classList.remove('collapsed');
                }
            }
        },
        {
            target: '[data-nav-id="profile"]',
            title: 'Your Profile',
            content: 'Access your profile settings here. Customize your preferences, update your information, and manage your account.'
        },
        {
            target: '.sidebar',
            title: 'Customize Your Sidebar',
            content: 'Pro tip: Go to your profile settings to enable sidebar edit mode. You can then drag to reorder navigation items and hide items you don\'t use!'
        },
        {
            target: '.main-content',
            title: 'You\'re All Set!',
            content: 'You\'re ready to start using VerAlign! Explore the interface and discover all the powerful features. You can replay this tutorial anytime from your profile settings.'
        }
    ];

    // Wait for page to load
    function startTutorialIfNeeded() {
        // Check if tutorial manager is available
        if (!window.tutorialManager) {
            console.warn('[Welcome Tutorial] Tutorial manager not loaded');
            return;
        }

        // Define the tutorial
        window.tutorialManager.defineTutorial(tutorialSteps);

        // Check if user is new (no tutorial completion recorded)
        if (!window.tutorialManager.hasCompleted()) {
            // Wait a moment for the page to fully render
            setTimeout(() => {
                console.log('[Welcome Tutorial] Starting tutorial for new user');
                window.tutorialManager.start(() => {
                    console.log('[Welcome Tutorial] Tutorial completed!');
                    // Optional: Show completion message
                    showCompletionMessage();
                });
            }, 1000);
        } else {
            console.log('[Welcome Tutorial] User has already completed the tutorial');
        }
    }

    // Show a completion message
    function showCompletionMessage() {
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = 'tutorial-completion-toast';
        toast.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 1rem;">
                <i class="fas fa-check-circle" style="color: #10b981; font-size: 1.5rem;"></i>
                <div>
                    <div style="font-weight: 600; margin-bottom: 0.25rem;">Tutorial Complete!</div>
                    <div style="font-size: 0.875rem; opacity: 0.8;">You're ready to use VerAlign</div>
                </div>
            </div>
        `;

        document.body.appendChild(toast);

        // Show toast
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
        });

        // Hide after 4 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 4000);
    }

    // Expose function to manually start tutorial
    window.startWelcomeTutorial = function() {
        if (window.tutorialManager) {
            window.tutorialManager.defineTutorial(tutorialSteps);
            window.tutorialManager.forceStart(() => {
                console.log('[Welcome Tutorial] Manual tutorial completed');
                showCompletionMessage();
            });
        } else {
            console.error('[Welcome Tutorial] Tutorial manager not available');
        }
    };

    // Expose function to reset tutorial
    window.resetWelcomeTutorial = function() {
        if (window.tutorialManager) {
            window.tutorialManager.reset();
            console.log('[Welcome Tutorial] Tutorial reset - will show on next page load');
        } else {
            console.error('[Welcome Tutorial] Tutorial manager not available');
        }
    };

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startTutorialIfNeeded);
    } else {
        startTutorialIfNeeded();
    }

    console.log('[Welcome Tutorial] Welcome tutorial script loaded');
})();
