function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");
    sidebar.classList.toggle("collapsed");
}

function logout() {
    const logoutForm = document.getElementById("logout-form");
    HTMLFormElement.prototype.submit.call(logoutForm);
}

// Sidebar Navigation Reordering and Customization
(function initSidebarReordering() {
    const STORAGE_KEY = 'sidebar_nav_order';
    const VISIBILITY_KEY = 'sidebar_nav_visibility';
    const EDIT_MODE_KEY = 'sidebar_edit_mode';
    let draggedElement = null;

    // Check if edit mode is enabled
    function isEditModeEnabled() {
        return sessionStorage.getItem(EDIT_MODE_KEY) === 'true';
    }

    // Load saved visibility state
    function loadVisibilityState() {
        try {
            const savedVisibility = localStorage.getItem(VISIBILITY_KEY);
            if (!savedVisibility) return;

            const visibility = JSON.parse(savedVisibility);
            const container = document.getElementById('draggable-nav-items');
            if (!container) return;

            Object.keys(visibility).forEach(id => {
                const item = container.querySelector(`[data-nav-id="${id}"]`);
                if (item) {
                    if (visibility[id] === false) {
                        item.classList.add('nav-item-hidden');
                    } else {
                        item.classList.remove('nav-item-hidden');
                    }
                }
            });

            console.log('[Sidebar] Loaded visibility state:', visibility);
        } catch (error) {
            console.error('[Sidebar] Error loading visibility state:', error);
        }
    }

    // Save visibility state
    function saveVisibilityState() {
        try {
            const container = document.getElementById('draggable-nav-items');
            if (!container) return;

            const items = container.querySelectorAll('.nav-item-draggable');
            const visibility = {};

            items.forEach(item => {
                const id = item.getAttribute('data-nav-id');
                if (id) {
                    visibility[id] = !item.classList.contains('nav-item-hidden');
                }
            });

            localStorage.setItem(VISIBILITY_KEY, JSON.stringify(visibility));
            console.log('[Sidebar] Saved visibility state:', visibility);
        } catch (error) {
            console.error('[Sidebar] Error saving visibility state:', error);
        }
    }

    // Toggle item visibility
    function toggleItemVisibility(navId) {
        const container = document.getElementById('draggable-nav-items');
        if (!container) return;

        const item = container.querySelector(`[data-nav-id="${navId}"]`);
        if (!item) return;

        item.classList.toggle('nav-item-hidden');
        saveVisibilityState();

        console.log('[Sidebar] Toggled visibility for:', navId);
    }

    // Get all navigation items with their state
    function getNavigationItems() {
        const container = document.getElementById('draggable-nav-items');
        if (!container) return [];

        const items = container.querySelectorAll('.nav-item-draggable');
        return Array.from(items).map(item => {
            const id = item.getAttribute('data-nav-id');
            const link = item.querySelector('.nav-link');
            const icon = link ? link.querySelector('i') : null;
            const text = link ? link.querySelector('span') : null;

            return {
                id: id,
                text: text ? text.textContent.trim() : '',
                icon: icon ? icon.className : '',
                visible: !item.classList.contains('nav-item-hidden'),
                element: item
            };
        });
    }

    // Reset to default order and visibility
    function resetToDefaults() {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(VISIBILITY_KEY);

        const container = document.getElementById('draggable-nav-items');
        if (!container) return;

        // Remove all hidden classes
        const items = container.querySelectorAll('.nav-item-draggable');
        items.forEach(item => {
            item.classList.remove('nav-item-hidden');
        });

        console.log('[Sidebar] Reset to defaults');

        // Reload the page to restore default order
        window.location.reload();
    }

    // Load saved order on page load
    function loadSavedOrder() {
        try {
            const savedOrder = localStorage.getItem(STORAGE_KEY);
            if (!savedOrder) return;

            const order = JSON.parse(savedOrder);
            const container = document.getElementById('draggable-nav-items');
            if (!container) return;

            // Create a map of current items by their data-nav-id
            const itemsMap = new Map();
            const items = container.querySelectorAll('.nav-item-draggable');
            items.forEach(item => {
                const id = item.getAttribute('data-nav-id');
                if (id) itemsMap.set(id, item);
            });

            // Reorder based on saved order
            order.forEach(id => {
                const item = itemsMap.get(id);
                if (item) {
                    container.appendChild(item);
                }
            });

            console.log('[Sidebar] Loaded saved navigation order:', order);
        } catch (error) {
            console.error('[Sidebar] Error loading saved order:', error);
        }
    }

    // Save current order to localStorage
    function saveOrder() {
        try {
            const container = document.getElementById('draggable-nav-items');
            if (!container) return;

            const items = container.querySelectorAll('.nav-item-draggable');
            const order = Array.from(items).map(item => item.getAttribute('data-nav-id'));

            localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
            console.log('[Sidebar] Saved navigation order:', order);
        } catch (error) {
            console.error('[Sidebar] Error saving order:', error);
        }
    }

    // Enable or disable edit mode
    function setEditMode(enabled) {
        const container = document.getElementById('draggable-nav-items');
        const sidebar = document.querySelector('.sidebar');

        if (enabled) {
            sessionStorage.setItem(EDIT_MODE_KEY, 'true');
            if (container) container.classList.add('edit-mode');
            if (sidebar) sidebar.classList.add('edit-mode');
            console.log('[Sidebar] Edit mode enabled');
        } else {
            sessionStorage.removeItem(EDIT_MODE_KEY);
            if (container) container.classList.remove('edit-mode');
            if (sidebar) sidebar.classList.remove('edit-mode');
            console.log('[Sidebar] Edit mode disabled');
        }
    }

    // Initialize drag-and-drop functionality
    function initDragAndDrop() {
        const container = document.getElementById('draggable-nav-items');
        if (!container) return;

        const draggableItems = container.querySelectorAll('.nav-item-draggable');

        draggableItems.forEach(item => {
            // Drag start - only allow if edit mode is enabled
            item.addEventListener('dragstart', (e) => {
                const editModeEnabled = isEditModeEnabled();
                console.log('[Sidebar] Dragstart event - Edit mode enabled:', editModeEnabled);
                console.log('[Sidebar] SessionStorage value:', sessionStorage.getItem(EDIT_MODE_KEY));

                if (!editModeEnabled) {
                    console.log('[Sidebar] Drag prevented - edit mode not enabled');
                    e.preventDefault();
                    return;
                }

                draggedElement = item;
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', item.innerHTML);
                console.log('[Sidebar] Drag started for:', item.getAttribute('data-nav-id'));
            });

            // Drag end
            item.addEventListener('dragend', () => {
                console.log('[Sidebar] Drag ended for:', item.getAttribute('data-nav-id'));
                item.classList.remove('dragging');

                // Remove all drag-over classes
                const allItems = container.querySelectorAll('.nav-item-draggable');
                allItems.forEach(i => i.classList.remove('drag-over'));

                // Save the new order
                saveOrder();
                draggedElement = null;
            });

            // Drag over
            item.addEventListener('dragover', (e) => {
                if (!isEditModeEnabled()) {
                    console.log('[Sidebar] Dragover blocked - edit mode not enabled');
                    return;
                }

                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';

                if (draggedElement && draggedElement !== item) {
                    // Remove drag-over from all items
                    const allItems = container.querySelectorAll('.nav-item-draggable');
                    allItems.forEach(i => i.classList.remove('drag-over'));

                    // Add drag-over to current item
                    item.classList.add('drag-over');

                    // Calculate if we should insert before or after
                    const rect = item.getBoundingClientRect();
                    const midpoint = rect.top + rect.height / 2;

                    const draggedId = draggedElement.getAttribute('data-nav-id');
                    const targetId = item.getAttribute('data-nav-id');

                    if (e.clientY < midpoint) {
                        console.log('[Sidebar] Moving', draggedId, 'before', targetId);
                        container.insertBefore(draggedElement, item);
                    } else {
                        console.log('[Sidebar] Moving', draggedId, 'after', targetId);
                        container.insertBefore(draggedElement, item.nextSibling);
                    }
                }
            });

            // Drag enter
            item.addEventListener('dragenter', (e) => {
                if (!isEditModeEnabled()) return;
                e.preventDefault();
            });

            // Drag leave
            item.addEventListener('dragleave', () => {
                item.classList.remove('drag-over');
            });

            // Drop
            item.addEventListener('drop', (e) => {
                if (!isEditModeEnabled()) return;

                e.preventDefault();
                e.stopPropagation();
                item.classList.remove('drag-over');
            });
        });

        console.log('[Sidebar] Drag-and-drop initialized for', draggableItems.length, 'items');
    }

    // Apply edit mode state on page load
    function applyEditModeState() {
        if (isEditModeEnabled()) {
            setEditMode(true);
        }
    }

    // Initialize toggle button (on settings page)
    function initToggleButton() {
        const toggleBtn = document.getElementById('toggle-sidebar-edit');
        const statusAlert = document.getElementById('sidebar-edit-status');

        if (!toggleBtn) return;

        // Update button state
        function updateButtonState() {
            const enabled = isEditModeEnabled();

            if (enabled) {
                toggleBtn.classList.remove('btn-outline-primary');
                toggleBtn.classList.add('btn-success');
                toggleBtn.innerHTML = '<i class="fas fa-check me-2"></i>Edit Mode Active';
                if (statusAlert) statusAlert.classList.remove('d-none');
            } else {
                toggleBtn.classList.remove('btn-success');
                toggleBtn.classList.add('btn-outline-primary');
                toggleBtn.innerHTML = '<i class="fas fa-edit me-2"></i>Enable Edit Mode';
                if (statusAlert) statusAlert.classList.add('d-none');
            }
        }

        // Toggle edit mode
        toggleBtn.addEventListener('click', () => {
            const newState = !isEditModeEnabled();
            setEditMode(newState);
            updateButtonState();
        });

        // Initialize button state
        updateButtonState();
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            loadSavedOrder();
            loadVisibilityState();
            initDragAndDrop();
            applyEditModeState();
            initToggleButton();
        });
    } else {
        loadSavedOrder();
        loadVisibilityState();
        initDragAndDrop();
        applyEditModeState();
        initToggleButton();
    }

    // Expose functions globally
    window.setSidebarEditMode = setEditMode;
    window.toggleSidebarItemVisibility = toggleItemVisibility;
    window.getSidebarNavigationItems = getNavigationItems;
    window.resetSidebarToDefaults = resetToDefaults;
})();

// Sidebar Recent Messages Live Updates
(function initSidebarMessagesPolling() {
    'use strict';

    // Check if user is authenticated
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    const chatList = sidebar.querySelector('.chat-list');
    if (!chatList) return;

    // Get username from the page - check multiple possible sources
    let currentUsername = null;

    // Try to get from data attribute on body or sidebar
    if (document.body.dataset.username) {
        currentUsername = document.body.dataset.username;
    } else if (sidebar.dataset.username) {
        currentUsername = sidebar.dataset.username;
    } else {
        // Try to extract from URL (works on most pages)
        const pathParts = window.location.pathname.split('/');
        // Look for common patterns like /message/{username}/ or /{app}/{username}/
        if (pathParts.length >= 3) {
            // Try different positions where username might be
            for (let i = 1; i < pathParts.length; i++) {
                if (pathParts[i] && pathParts[i] !== 'message' && pathParts[i] !== 'conversation' &&
                    pathParts[i] !== 'dashboard' && pathParts[i] !== 'teams' && pathParts[i] !== 'projects' &&
                    !pathParts[i].match(/^\d+$/)) {
                    currentUsername = pathParts[i];
                    break;
                }
            }
        }
    }

    // If we still don't have username, try to get it from a link in the sidebar
    if (!currentUsername) {
        const messageLink = sidebar.querySelector('a[href*="/message/"]');
        if (messageLink) {
            const match = messageLink.href.match(/\/message\/([^\/]+)\//);
            if (match) {
                currentUsername = match[1];
            }
        }
    }

    if (!currentUsername) {
        console.log('[Sidebar Messages] Could not determine username, polling disabled');
        return;
    }

    console.log('[Sidebar Messages] Initializing live updates for user:', currentUsername);

    // Function to update the sidebar recent messages
    function updateSidebarMessages(conversations) {
        if (!chatList) return;

        // Clear current list
        chatList.innerHTML = '';

        if (!conversations || conversations.length === 0) {
            chatList.innerHTML = `
                <div class="text-white-50 text-center py-3">
                    <small>No recent messages</small>
                </div>
            `;
            return;
        }

        // Create HTML for each conversation
        conversations.forEach(conv => {
            const chatItem = document.createElement('a');
            chatItem.href = `/message/${currentUsername}/conversation/${conv.id}/`;
            chatItem.className = 'chat-item text-decoration-none';

            chatItem.innerHTML = `
                <img src="${conv.avatar_url || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(conv.name) + '&background=random'}"
                     alt="${escapeHtml(conv.name)}"
                     class="rounded-circle"
                     width="32"
                     height="32"/>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="fw-medium text-white">${truncateText(escapeHtml(conv.name), 20)}</div>
                        ${conv.last_message_time ? `<small class="text-white-50">${escapeHtml(conv.last_message_time)}</small>` : ''}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-white-50">${truncateText(escapeHtml(conv.last_message_preview), 30)}</small>
                        ${conv.unread_count > 0 ? `<span class="badge bg-primary rounded-pill">${conv.unread_count}</span>` : ''}
                    </div>
                </div>
            `;

            chatList.appendChild(chatItem);
        });
    }

    // Helper function to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Helper function to truncate text
    function truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    // Function to poll for sidebar updates
    function pollSidebarConversations() {
        fetch(`/message/${currentUsername}/poll-sidebar/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.conversations) {
                    updateSidebarMessages(data.conversations);
                }
            })
            .catch(error => {
                // Silently fail - don't spam console on auth errors or network issues
                if (error.message.includes('403') || error.message.includes('401')) {
                    // User not authenticated, stop polling
                    console.log('[Sidebar Messages] Authentication error, stopping polls');
                    if (pollInterval) {
                        clearInterval(pollInterval);
                    }
                }
            });
    }

    // Start polling every 3 seconds
    const pollInterval = setInterval(pollSidebarConversations, 3000);

    // Do an initial poll after 1 second
    setTimeout(pollSidebarConversations, 1000);

    // Clean up interval when page is closed/navigated away
    window.addEventListener('beforeunload', function() {
        clearInterval(pollInterval);
    });

    console.log('[Sidebar Messages] Live updates initialized, polling every 3 seconds');
})();