document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/users')
    .then(response => response.json())
    .then(data => {
      const profileList = document.getElementById('profile-list');
      const status = document.getElementById('status');
      
      if (Object.keys(data).length === 0) {
        status.textContent = 'There are no new posts.';
      } else {
        status.textContent = `Showing updates for ${Object.keys(data).length} users.`;
      }

      // Sort profiles by most recent post
      const sortedProfiles = Object.entries(data).sort((a, b) => {
        const dateA = a[1].last_post_date ? new Date(a[1].last_post_date) : new Date(0);
        const dateB = b[1].last_post_date ? new Date(b[1].last_post_date) : new Date(0);
        return dateB - dateA;
      });

      for (const [username, userData] of sortedProfiles) {
        const profileCard = createProfileCard(username, userData);
        profileList.appendChild(profileCard);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('status').textContent = 'Error loading data.';
    });
});

function createProfileCard(username, userData) {
  const card = document.createElement('div');
  card.className = 'profile';
  
  const imageUrl = `/proxy?url=${encodeURIComponent(userData.profile_pic_url)}`;
  
  const daysAgo = userData.last_post_date ? getDaysAgo(userData.last_post_date) : null;
  const secondsAgo = userData.last_post_date ? getSecondsAgo(userData.last_post_date) : null; 
  if (daysAgo !== null && daysAgo < 7) {
    card.classList.add('recent-post');
  }

  card.innerHTML = `
    <img src="${imageUrl}" alt="${username}'s profile picture" class="profile-pic">
    <div class="profile-info">
      <h2>${userData.name}</h2>
      <p>@${username}</p>
      <p>${userData.bio || ''}</p>
    </div>
    <div class="bottom-row">
      <a href="https://www.instagram.com/${username}" target="_blank">Profile</a>
      <p>${formatTimeAgo(secondsAgo) ? `Last posted ${formatTimeAgo(secondsAgo)}` : 'No posts'}</p>
    </div>
  `;

  return card;
}

function getDaysAgo(dateString) {
  const postDate = new Date(dateString);
  const today = new Date();
  const diffTime = Math.abs(today - postDate);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
}


function formatTimeAgo(seconds) {
  if (!seconds) { return ""}
  const diffMin = Math.floor(seconds / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffDay > 0) {
    return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
  } else if (diffHour > 0) {
    return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
  } else if (diffMin > 0) {
    return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  }  
  else {
    return 'Just now';
  }
}


function getSecondsAgo(dateString) {
  const postDate = new Date(dateString);
  const now = new Date();
  const diffMs = now - postDate;
  return Math.floor(diffMs / 1000);
}