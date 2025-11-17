// Message UI JavaScript
(function() {
  'use strict';

  // Make conversations clickable
  const conversationItems = document.querySelectorAll('.conversation-item');
  conversationItems.forEach(item => {
    item.addEventListener('click', function() {
      // Remove active class from all conversations
      conversationItems.forEach(conv => conv.classList.remove('active'));

      // Add active class to clicked conversation
      this.classList.add('active');

      // Here you would typically load the conversation messages
      // For now, we'll just update the thread header
      const conversationId = this.dataset.conversationId;
      const conversationName = this.querySelector('.conversation-name').textContent;
      const conversationAvatar = this.querySelector('.conversation-avatar img')?.src ||
                                  this.querySelector('.team-avatar');

      // Update thread header (if you want to show different conversations)
      console.log(`Switched to conversation: ${conversationName}`);
    });
  });

  // User search functionality
  const recipientSearch = document.getElementById('recipientSearch');
  const userSearchResults = document.getElementById('userSearchResults');
  let searchTimeout;

  if (recipientSearch) {
    recipientSearch.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      const query = this.value.trim();

      if (query.length < 2) {
        userSearchResults.classList.remove('active');
        userSearchResults.innerHTML = '';
        return;
      }

      searchTimeout = setTimeout(() => {
        fetch(`/api/users/search/?q=${encodeURIComponent(query)}`)
          .then(response => response.json())
          .then(data => {
            if (data.users && data.users.length > 0) {
              renderUserResults(data.users);
            } else {
              userSearchResults.innerHTML = '<div class="p-3 text-muted text-center">No users found</div>';
              userSearchResults.classList.add('active');
            }
          })
          .catch(error => {
            console.error('Error searching users:', error);
          });
      }, 300);
    });
  }

  function renderUserResults(users) {
    const html = users.map(user => `
      <div class="user-result-item" onclick="startConversationWith('${user.username}')">
        <div class="user-result-avatar">
          <img src="${user.avatar || `https://ui-avatars.com/api/?name=${user.full_name || user.username}&background=random`}"
               alt="${user.full_name || user.username}"
               class="rounded-circle">
        </div>
        <div class="user-result-info">
          <h6>${user.full_name || user.username}</h6>
          <small>@${user.username}</small>
        </div>
      </div>
    `).join('');

    userSearchResults.innerHTML = html;
    userSearchResults.classList.add('active');
  }

  window.startConversationWith = function(otherUsername) {
    // Get current username from the page URL or a data attribute
    const currentUsername = window.location.pathname.split('/')[2]; // Extract from /messages/{username}/
    window.location.href = `/messages/${currentUsername}/start/${otherUsername}/`;
  };

  // Close search results when clicking outside
  document.addEventListener('click', function(e) {
    if (userSearchResults && !recipientSearch.contains(e.target) && !userSearchResults.contains(e.target)) {
      userSearchResults.classList.remove('active');
    }
  });

  // Message form submission with AJAX (optional enhancement)
  const messageForm = document.getElementById('messageForm');
  if (messageForm) {
    messageForm.addEventListener('submit', function(e) {
      // Let the form submit normally for now
      // Could be enhanced with AJAX later
    });
  }

  // Typing indicator (placeholder for WebSocket implementation)
  const messageInput = document.getElementById('messageInput');
  let typingTimeout;

  if (messageInput) {
    messageInput.addEventListener('input', function() {
      clearTimeout(typingTimeout);

      // Send typing indicator to server via WebSocket
      // sendTypingIndicator(true);

      typingTimeout = setTimeout(() => {
        // Stop typing indicator
        // sendTypingIndicator(false);
      }, 1000);
    });
  }

  // Auto-update conversation list (polling - could be replaced with WebSockets)
  function pollForNewMessages() {
    const conversationsList = document.getElementById('conversationsList');
    if (!conversationsList) return;

    setInterval(() => {
      // Fetch new messages and update UI
      // This is a placeholder for WebSocket implementation
      console.log('Polling for new messages...');
    }, 30000); // Poll every 30 seconds
  }

  // Initialize polling if on messages page
  if (document.querySelector('.messages-container')) {
    // pollForNewMessages(); // Uncomment when backend is ready
  }

  // Smooth scroll to bottom when new message arrives
  function scrollToBottom() {
    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
      messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
      });
    }
  }

  // Observe new messages and scroll
  const messagesContainer = document.getElementById('messagesContainer');
  if (messagesContainer) {
    const observer = new MutationObserver(() => {
      scrollToBottom();
    });

    observer.observe(messagesContainer, {
      childList: true,
      subtree: true
    });
  }

  // Handle file attachments (placeholder)
  const attachmentBtn = document.querySelector('.attachment-btn');
  if (attachmentBtn) {
    attachmentBtn.addEventListener('click', function() {
      // Open file picker
      console.log('Open file picker');
    });
  }

  // Handle emoji picker (placeholder)
  const emojiBtn = document.querySelector('.emoji-btn');
  if (emojiBtn) {
    emojiBtn.addEventListener('click', function() {
      // Open emoji picker
      console.log('Open emoji picker');
    });
  }
})();
