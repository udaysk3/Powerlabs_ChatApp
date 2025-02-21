// messaging.js
document.addEventListener('DOMContentLoaded', function() {
    // Check if user-data element exists to prevent initial error
    const userDataElement = document.getElementById('user-data');
    if (!userDataElement) {
        console.error('User data element not found. Adding user-data placeholder...');
        const userDataPlaceholder = document.createElement('script');
        userDataPlaceholder.id = 'user-data';
        userDataPlaceholder.type = 'application/json';
        userDataPlaceholder.textContent = JSON.stringify({
            id: 0,
            name: 'Unknown User',
            role: 'client'
        });
        document.body.appendChild(userDataPlaceholder);
    }
    
    const currentUser = JSON.parse(document.getElementById('user-data').textContent);
    let currentConversation = null;
    let quoteData = null;
    let profileData = null;
    let chatSocket = null;
    
    // Function to establish WebSocket connection
    function setupWebSocket(conversationId) {
        // Don't try to reconnect if we don't have a conversation ID
        if (!conversationId) {
            console.log('No conversation ID provided for WebSocket');
            return;
        }
        
        // Close existing connection if any
        if (chatSocket) {
            // Only close if it's not already closing or closed
            if (chatSocket.readyState !== WebSocket.CLOSING && 
                chatSocket.readyState !== WebSocket.CLOSED) {
                chatSocket.close();
            }
        }
        
        // Create new WebSocket connection with a proper protocol
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const wsUrl = wsProtocol + '127.0.0.1:8081/ws/chat/' + conversationId + '/';
        
        try {
            chatSocket = new WebSocket(wsUrl);
            // Setup event handlers
            chatSocket.onopen = function() {
                console.log('WebSocket connection established for conversation:', conversationId);
                // Mark the conversation as active/read when WebSocket connects
                markConversationAsRead(conversationId);
            };
            
            chatSocket.onmessage = function(e) {
                try {
                    console.log("Received WebSocket message:", e.data);
                    const data = JSON.parse(e.data);
                    if (data.type === 'new_message' && data.conversation_id == currentConversation) {
                        appendMessage(data.message);
                        scrollToBottom();
                    } else if (data.type === 'new_message' && data.conversation_id != currentConversation) {
                        // Update conversation list to show unread message
                        console.log('Received message for different conversation:', data.conversation_id);
                        updateConversationUnread(data.conversation_id);
                    }
                    else{
                        console.log('Received message for no conversation:', data.conversation_id);
                        updateConversationUnread(data.conversation_id);
                    }
                } catch (error) {
                    console.error('Error processing WebSocket message:', error);
                }
            };
            
            let reconnectAttempts = 0;
            const maxReconnectAttempts = 5;
            
            chatSocket.onclose = function(e) {
                console.log('WebSocket closed:', e.code, e.reason);
                
                if (reconnectAttempts < maxReconnectAttempts) {
                    // Exponential backoff for reconnection
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    console.log(`Attempting to reconnect in ${delay/1000} seconds...`);
                    
                    setTimeout(function() {
                        reconnectAttempts++;
                        setupWebSocket(currentConversation);
                    }, delay);
                } else {
                    console.error('Maximum reconnection attempts reached.');
                    // Show offline indicator to user
                    const statusElement = document.getElementById('connection-status');
                    if (statusElement) {
                        statusElement.innerHTML = '<span class="text-danger">⚠️ Offline</span>';
                        statusElement.style.display = 'block';
                    }
                }
            };
            
            chatSocket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
        }
    }
    
    // Add this function to mark conversations as read
    function markConversationAsRead(conversationId) {
        fetch(`/chat/api/mark-read/${conversationId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                // Update UI to remove unread indicator
                const conversationItem = document.querySelector(`.conversation-item[data-id="${conversationId}"]`);
                if (conversationItem) {
                    conversationItem.classList.remove('unread');
                    const badge = conversationItem.querySelector('.unread-badge');
                    if (badge) {
                        badge.remove();
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error marking conversation as read:', error);
        });
    }
    
    // Load conversations
    function loadConversations() {
        fetch('/chat/api/conversations/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(conversations => {
                const conversationList = document.getElementById('conversation-list');
                conversationList.innerHTML = '';
                
                if (conversations.length === 0) {
                    conversationList.innerHTML = '<div class="p-3 text-center text-muted">No conversations found</div>';
                    return;
                }
                
                conversations.forEach(conversation => {
                    // Determine if this is a client or supplier view
                    let otherParticipant = conversation.participants.find(p => p.id !== currentUser.id);
                    
                    // Skip if we can't determine the other participant
                    if (!otherParticipant) {
                        console.warn('Could not find other participant in conversation:', conversation);
                        return;
                    }
                    
                    const conversationItem = document.createElement('div');
                    conversationItem.className = 'list-group-item conversation-item';
                    if (conversation.unread_count > 0) {
                        conversationItem.classList.add('unread');
                    }
                    conversationItem.dataset.id = conversation.id;
                    
                    // Format based on user role (client or supplier)
                    let nameDisplay = currentUser.role === 'client' ? 
                        `<strong>${otherParticipant.company_name || 'Company'}</strong>` : 
                        `<strong>${otherParticipant.name || 'User'}</strong>`;
                    
                    let subtitleDisplay = currentUser.role === 'client' ? 
                        (otherParticipant.contact_name || 'Contact') : 
                        (otherParticipant.location || 'Location');
                    
                    const lastMessageTime = formatRelativeTime(new Date(conversation.last_message_time));
                    
                    conversationItem.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 style="color:#000"> ${nameDisplay} </h6>
                                <div class="text-muted">${subtitleDisplay}</div>
                                <small class="last-message-time">${lastMessageTime}</small>
                            </div>
                            ${conversation.unread_count > 0 ? 
                                `<span class="unread-badge">${conversation.unread_count}</span>` : ''}
                        </div>
                    `;
                    
                    conversationItem.addEventListener('click', function() {
                        document.querySelectorAll('.conversation-item').forEach(item => {
                            item.classList.remove('active');
                        });
                        this.classList.add('active');
                        this.classList.remove('unread');
                        const conversationId = this.dataset.id;
                        loadConversation(conversationId);
                    });
                    
                    conversationList.appendChild(conversationItem);
                });
                
                // If there's at least one conversation, load the first one
                if (conversations.length > 0) {
                    const firstConversation = conversations[0];
                    document.querySelector(`.conversation-item[data-id="${firstConversation.id}"]`).classList.add('active');
                    loadConversation(firstConversation.id);
                }
            })
            .catch(error => {
                console.error('Error loading conversations:', error);
                document.getElementById('conversation-list').innerHTML = 
                    '<div class="p-3 text-center text-danger">Failed to load conversations. Please try refreshing the page.</div>';
            });
    }
    
    // Load a specific conversation
    function loadConversation(conversationId) {
        currentConversation = conversationId;
        
        // Set up WebSocket for this conversation
        setupWebSocket(conversationId);
        
        // Clear current messages
        const messageList = document.getElementById('message-list');
        messageList.innerHTML = '';
        
        // Show loading indicator
        messageList.innerHTML = '<div class="text-center p-3"><span class="spinner-border text-primary" role="status"></span></div>';
        
        // Load conversation details and quote info
        fetch(`/chat/api/conversations/${conversationId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                // Clear loading indicator
                messageList.innerHTML = '';
                
                // Update conversation header
                const otherParticipant = data.participants.find(p => p.id !== currentUser.id);
                if (otherParticipant) {
                    document.getElementById('current-chat-name').textContent = 
                        currentUser.role === 'client' ? 
                            (otherParticipant.company_name || 'Company') : 
                            (otherParticipant.name || 'User');
                    document.getElementById('current-chat-subtitle').textContent = 
                        currentUser.role === 'client' ? 
                            (otherParticipant.contact_name || 'Contact') : 
                            (otherParticipant.location || 'Location');
                    
                    // Load profile data
                    profileData = otherParticipant;
                    updateProfileDetails();
                }
                
                // Load messages
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(message => {
                        appendMessage(message);
                    });
                } else {
                    messageList.innerHTML = '<div class="text-center text-muted p-3">No messages yet. Start the conversation!</div>';
                }
                
                // Load quote data
                quoteData = data.quote;
                updateQuoteDetails();
                
                scrollToBottom();
            })
            .catch(error => {
                console.error('Error loading conversation:', error);
                messageList.innerHTML = '<div class="text-center text-danger p-3">Failed to load messages. Please try again.</div>';
            });
    }
    
    // Append a message to the message list
    function appendMessage(message) {
        if (!message || !message.sender) {
            console.warn('Attempted to append invalid message:', message);
            return;
        }
        
        const messageList = document.getElementById('message-list');
        const isOutgoing = message.sender.id === currentUser.id;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isOutgoing ? 'outgoing' : 'incoming'}`;
        
        const formattedTime = formatRelativeTime(new Date(message.timestamp));
        
        messageElement.innerHTML = `
            <div class="message-sender">${message.sender.name || 'User'}</div>
            <div class="message-content">${escapeHTML(message.content)}</div>
            <div class="message-timestamp">${formattedTime}</div>
        `;
        
        messageList.appendChild(messageElement);
    }
    
    // Helper function to escape HTML to prevent XSS
    function escapeHTML(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
    
    // Update the quote details in the right column
    function updateQuoteDetails() {
        const quoteElements = {
            'quote-price': document.getElementById('quote-price'),
            'quote-hardware': document.getElementById('quote-hardware'),
            'quote-need-met': document.getElementById('quote-need-met'),
            'quote-payback': document.getElementById('quote-payback'),
            'quote-funding': document.getElementById('quote-funding'),
            'full-quote-link': document.getElementById('full-quote-link')
        };
        
        // Ensure all elements exist
        const allElementsExist = Object.values(quoteElements).every(element => element !== null);
        
        if (!allElementsExist) {
            console.warn('Some quote detail elements are missing in the DOM');
            return;
        }
        
        if (!quoteData) {
            // Hide or show placeholder if no quote data
            Object.values(quoteElements).forEach(el => {
                if (el.id === 'full-quote-link') {
                    el.style.display = 'none';
                } else {
                    el.textContent = 'N/A';
                }
            });
            return;
        }
        
        // Update with actual quote data
        quoteElements['quote-price'].textContent = `${quoteData.price || 0} $`;
        quoteElements['quote-hardware'].textContent = quoteData.model || 'Not specified';
        quoteElements['quote-need-met'].textContent = `${quoteData.need_met || 0}%`;
        quoteElements['quote-payback'].textContent = quoteData.payback_period || 'Not calculated';
        quoteElements['quote-funding'].textContent = quoteData.funding || 'Not specified';
        
        // Set the link to the full quote page
        quoteElements['full-quote-link'].href = `/quotes/${quoteData.id}/`;
        quoteElements['full-quote-link'].style.display = 'inline-block';
    }
    
    // Update the profile details in the right column
    function updateProfileDetails() {
        const profileElements = {
            'company-name': document.getElementById('company-name'),
            'company-location': document.getElementById('company-location'),
            'rating-section': document.getElementById('rating-section'),
            'rating-value': document.getElementById('rating-value'),
            'rating-stars': document.getElementById('rating-stars'),
            'review-count': document.getElementById('review-count')
        };
        
        // Ensure all elements exist
        const allElementsExist = Object.values(profileElements).every(element => element !== null);
        
        if (!allElementsExist) {
            console.warn('Some profile detail elements are missing in the DOM');
            return;
        }
        
        if (!profileData) {
            profileElements['company-name'].textContent = 'No profile data';
            profileElements['company-location'].textContent = '';
            profileElements['rating-section'].style.display = 'none';
            return;
        }
        
        // Set company/client name
        profileElements['company-name'].textContent = 
            currentUser.role === 'client' ? 
                (profileData.company_name || 'Company') : 
                (profileData.name || 'User');
        
        // Set location info
        profileElements['company-location'].textContent = profileData.location || 'Location not provided';
        
        // If supplier and has rating, show rating
        if (currentUser.role === 'client' && profileData.rating) {
            profileElements['rating-section'].style.display = 'block';
            profileElements['rating-value'].textContent = profileData.rating.toFixed(1);
            
            // Generate stars
            const starsContainer = profileElements['rating-stars'];
            starsContainer.innerHTML = '';
            const rating = profileData.rating;
            for (let i = 1; i <= 5; i++) {
                const star = document.createElement('i');
                if (i <= rating) {
                    star.className = 'fas fa-star';
                } else if (i - 0.5 <= rating) {
                    star.className = 'fas fa-star-half-alt';
                } else {
                    star.className = 'far fa-star';
                }
                starsContainer.appendChild(star);
            }
            
            // Show review count
            profileElements['review-count'].textContent = 
                `${profileData.review_count || 0} reviews`;
        } else {
            profileElements['rating-section'].style.display = 'none';
        }
    }
    
    // Handle sending messages
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    
    if (!messageInput || !sendButton) {
        console.error('Message input or send button not found');
    } else {
        function sendMessage() {
            if (!currentConversation || !messageInput.value.trim()) return;
            
            const messageContent = messageInput.value.trim();
            
            // Disable input and button while sending
            messageInput.disabled = true;
            sendButton.disabled = true;
            
            fetch('/chat/api/send-message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    conversation_id: currentConversation,
                    content: messageContent
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to send message: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                // Clear input field
                messageInput.value = '';
                // Message will be added via WebSocket
            })
            .catch(error => {
                console.error('Error sending message:', error);
                alert('Failed to send message. Please try again.');
            })
            .finally(() => {
                // Re-enable input and button
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.focus();
            });
        }
        
        sendButton.addEventListener('click', sendMessage);
        
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-conversations');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query) {
                searchConversations(query);
            } else {
                loadConversations();
            }
        });
    }
    
    function searchConversations(query) {
        fetch(`/chat/api/search/?type=conversations&q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Search request failed: ' + response.statusText);
                }
                return response.json();
            })
            .then(results => {
                const conversationList = document.getElementById('conversation-list');
                conversationList.innerHTML = '';
                
                if (results.length === 0) {
                    conversationList.innerHTML = '<div class="p-3 text-center text-muted">No results found</div>';
                    return;
                }
                
                results.forEach(conversation => {
                    // Similar code to loadConversations but filtered by search results
                    let otherParticipant = conversation.participants.find(p => p.id !== currentUser.id);
                    
                    if (!otherParticipant) return;
                    
                    const conversationItem = document.createElement('div');
                    conversationItem.className = 'list-group-item conversation-item';
                    if (conversation.unread_count > 0) {
                        conversationItem.classList.add('unread');
                    }
                    conversationItem.dataset.id = conversation.id;
                    
                    let nameDisplay = currentUser.role === 'client' ? 
                        `<strong>${otherParticipant.company_name || 'Company'}</strong>` : 
                        `<strong>${otherParticipant.name || 'User'}</strong>`;
                    
                    let subtitleDisplay = currentUser.role === 'client' ? 
                        (otherParticipant.contact_name || 'Contact') : 
                        (otherParticipant.location || 'Location');
                    
                    const lastMessageTime = formatRelativeTime(new Date(conversation.last_message_time));
                    
                    conversationItem.innerHTML = `
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                ${nameDisplay}
                                <div class="text-muted">${subtitleDisplay}</div>
                                <small class="last-message-time">${lastMessageTime}</small>
                            </div>
                            
                            ${conversation.unread_count > 0 ? 
                                `<span class="unread-badge">${conversation.unread_count}</span>` : ''}
                        </div>
                    `;
                    
                    conversationItem.addEventListener('click', function() {
                        document.querySelectorAll('.conversation-item').forEach(item => {
                            item.classList.remove('active');
                        });
                        this.classList.add('active');
                        this.classList.remove('unread');
                        loadConversation(this.dataset.id);
                    });
                    
                    conversationList.appendChild(conversationItem);
                });
            })
            .catch(error => {
                console.error('Error searching conversations:', error);
                document.getElementById('conversation-list').innerHTML = 
                    '<div class="p-3 text-center text-danger">Search failed. Please try again.</div>';
            });
    }
    
    // Helper function to format relative time (e.g., "5 minutes ago")
    function formatRelativeTime(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);
        
        if (diffSec < 60) {
            return 'just now';
        } else if (diffMin < 60) {
            return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
        } else if (diffHour < 24) {
            return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
        } else {
            return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
        }
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Function to scroll message container to bottom
    function scrollToBottom() {
        const messageList = document.getElementById('message-list');
        if (messageList) {
            messageList.scrollTop = messageList.scrollHeight;
        }
    }
    
    function updateConversationUnread(conversationId) {
        // Fetch all unread counts from the server
        console.log('Updating unread counts...');
        fetch('/chat/api/unread-counts/')
            .then(response => response.json())
            .then(unreadCounts => {
                console.log("unread counts", unreadCounts);
                // Update the specific conversation that just received a message
                const conversationItem = document.querySelector(`.conversation-item[data-id="${conversationId}"]`);
                if (conversationItem) {
                    conversationItem.classList.add('unread');
                    // Get accurate count from server response
                    const unreadCount = unreadCounts[conversationId] || 0;
                    
                    // Update or add unread badge
                    let badge = conversationItem.querySelector('.unread-badge');
                    if (badge) {
                        badge.textContent = unreadCount;
                    } else if (unreadCount > 0) {
                        const badgeContainer = document.createElement('span');
                        badgeContainer.className = 'unread-badge';
                        badgeContainer.textContent = unreadCount;
                        const flexContainer = conversationItem.querySelector('.d-flex');
                        if (flexContainer) {
                            flexContainer.appendChild(badgeContainer);
                        }
                    }
                }
                
                // Also update any other conversations that might have unread messages
                Object.entries(unreadCounts).forEach(([convId, count]) => {
                    if (convId != conversationId && count > 0) {
                        const otherConvItem = document.querySelector(`.conversation-item[data-id="${convId}"]`);
                        if (otherConvItem) {
                            otherConvItem.classList.add('unread');
                            let otherBadge = otherConvItem.querySelector('.unread-badge');
                            if (otherBadge) {
                                otherBadge.textContent = count;
                            } else {
                                const newBadge = document.createElement('span');
                                newBadge.className = 'unread-badge';
                                newBadge.textContent = count;
                                const flexDiv = otherConvItem.querySelector('.d-flex');
                                if (flexDiv) {
                                    flexDiv.appendChild(newBadge);
                                }
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching unread counts:', error);
            });
    }

    // Function to periodically refresh unread counts
function refreshUnreadCounts() {
    console.log('Refreshing unread counts...');
    fetch('/chat/api/unread-counts/')
        .then(response => response.json())
        .then(unreadCounts => {
            Object.entries(unreadCounts).forEach(([convId, count]) => {
                const convItem = document.querySelector(`.conversation-item[data-id="${convId}"]`);
                if (convItem && count > 0) {
                    convItem.classList.add('unread');
                    let badge = convItem.querySelector('.unread-badge');
                    if (badge) {
                        badge.textContent = count;
                    } else {
                        const newBadge = document.createElement('span');
                        newBadge.className = 'unread-badge';
                        newBadge.textContent = count;
                        const flexDiv = convItem.querySelector('.d-flex');
                        if (flexDiv) {
                            flexDiv.appendChild(newBadge);
                        }
                    }
                } else if (convItem && count === 0) {
                    convItem.classList.remove('unread');
                    const badge = convItem.querySelector('.unread-badge');
                    if (badge) {
                        badge.remove();
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error refreshing unread counts:', error);
        });
}

// Add this to your initialization code
loadConversations();
refreshUnreadCounts(); // Initial refresh

// Set up periodic refresh of unread counts (every 30 seconds)
const unreadRefreshInterval = setInterval(refreshUnreadCounts, 30000);
});