function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");
    sidebar.classList.toggle("collapsed");
}

function logout() {
    const logoutForm = document.getElementById("logout-form");
    HTMLFormElement.prototype.submit.call(logoutForm);
}

// Sidebar Navigation Reordering
(function initSidebarReordering() {
    const STORAGE_KEY = 'sidebar_nav_order';
    const EDIT_MODE_KEY = 'sidebar_edit_mode';
    let draggedElement = null;

    // Check if edit mode is enabled
    function isEditModeEnabled() {
        return sessionStorage.getItem(EDIT_MODE_KEY) === 'true';
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
                if (!isEditModeEnabled()) {
                    e.preventDefault();
                    return;
                }

                draggedElement = item;
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', item.innerHTML);
            });

            // Drag end
            item.addEventListener('dragend', () => {
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
                if (!isEditModeEnabled()) return;

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

                    if (e.clientY < midpoint) {
                        container.insertBefore(draggedElement, item);
                    } else {
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
            initDragAndDrop();
            applyEditModeState();
            initToggleButton();
        });
    } else {
        loadSavedOrder();
        initDragAndDrop();
        applyEditModeState();
        initToggleButton();
    }

    // Expose setEditMode globally for debugging
    window.setSidebarEditMode = setEditMode;
})();