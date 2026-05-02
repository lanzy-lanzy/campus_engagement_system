// Custom JavaScript for Campus Voice
document.addEventListener('DOMContentLoaded', function() {
  initMentions();
});

function initMentions() {
  // HTMX config
  htmx.config.defaultSwapStyle = 'outerHTML';
  
  document.body.addEventListener('htmx:configRequest', function(evt) {
    const csrfMatch = document.cookie.match(/csrftoken=([^;]+)/);
    if (csrfMatch) {
      evt.detail.headers['X-CSRFToken'] = csrfMatch[1];
    }
  });

  // Mentions - run on DOMContentLoaded
  const fields = document.querySelectorAll('[data-mentions]');
  fields.forEach(initMentionField);

  // Also run on HTMX swap for dynamically loaded content
  document.body.addEventListener('htmx:afterSwap', function() {
    document.querySelectorAll('[data-mentions]').forEach(initMentionField);
  });
}

function initMentionField(textarea) {
  if (textarea.dataset.mentionInit) return;
  textarea.dataset.mentionInit = 'true';

  let dropdown = null;
  let friends = [];

  textarea.addEventListener('input', handleInput);
  textarea.addEventListener('keydown', handleKeydown);

  function handleInput(e) {
    const pos = textarea.selectionStart;
    const text = textarea.value;
    const before = text.slice(0, pos);
    const match = before.match(/@(\w*)$/);
    
    if (match) {
      showDropdown(match[1]);
    } else {
      hideDropdown();
    }
  }

  function handleKeydown(e) {
    if (dropdown && !dropdown.classList.contains('hidden')) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateDown();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateUp();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        selectCurrent();
      } else if (e.key === 'Escape') {
        hideDropdown();
      }
    }
  }

  function showDropdown(q) {
  fetch(`/accounts/friends/search/?q=${encodeURIComponent(q)}`)
    .then(r => r.json())
    .then(data => {
      friends = data;
      if (friends.length === 0) {
        hideDropdown();
        return;
      }
      if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.className = 'mention-dropdown hidden';
        dropdown.style.cssText = 'position:absolute;top:100%;left:0;margin-top:4px;background:white;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:9999;min-width:200px;max-height:200px;overflow-y:auto;';
        textarea.parentNode.style.cssText = 'position:relative;';
        textarea.parentNode.appendChild(dropdown);
      }
      renderList();
      dropdown.classList.remove('hidden');
    });
}

  function renderList() {
  const q = (textarea.value.slice(0, textarea.selectionStart).match(/@(\w*)$/) || ['',''])[1].toLowerCase();
  dropdown.innerHTML = friends.map((f, i) => {
    const nameIdx = f.username.toLowerCase().indexOf(q);
    let nameHtml = f.username;
    if (q && nameIdx >= 0) {
      nameHtml = f.username.slice(0, nameIdx) + '<strong class="text-blue-600 font-semibold">' + 
               f.username.slice(nameIdx, nameIdx + q.length) + '</strong>' + 
               f.username.slice(nameIdx + q.length);
    }
    return `<div class="mention-item px-3 py-2 cursor-pointer hover:bg-gray-100 flex items-center gap-3" data-index="${i}">
      <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-semibold">${f.username.charAt(0).toUpperCase()}</div>
      <span class="text-sm" style="font-size:14px;">${nameHtml}</span>
    </div>`;
  }).join('');
  dropdown.querySelectorAll('[data-index]').forEach(el => {
    el.addEventListener('mousedown', (e) => {
      e.preventDefault();
      selectFriend(parseInt(el.dataset.index));
    });
  });
}

  function navigateDown() {
    const items = dropdown.querySelectorAll('.mention-item');
    const current = dropdown.querySelector('.mention-item.bg-gray-100');
    if (current) current.classList.remove('bg-gray-100');
    let idx = Array.from(items).indexOf(current);
    idx = (idx + 1) % items.length;
    items[idx]?.classList.add('bg-gray-100');
  }

  function navigateUp() {
    const items = dropdown.querySelectorAll('.mention-item');
    const current = dropdown.querySelector('.mention-item.bg-gray-100');
    if (current) current.classList.remove('bg-gray-100');
    let idx = Array.from(items).indexOf(current);
    idx = idx <= 0 ? items.length - 1 : idx - 1;
    items[idx]?.classList.add('bg-gray-100');
  }

  function selectCurrent() {
    const items = dropdown.querySelectorAll('.mention-item');
    const current = dropdown.querySelector('.mention-item.bg-gray-100');
    if (current) {
      const idx = parseInt(current.dataset.index);
      selectFriend(idx);
    }
  }

  function selectFriend(idx) {
    const friend = friends[idx];
    if (!friend) return;
    const pos = textarea.selectionStart;
    const text = textarea.value;
    const before = text.slice(0, pos).replace(/@\w*$/, `@${friend.username} `);
    const after = text.slice(pos);
    textarea.value = before + after;
    textarea.selectionStart = textarea.selectionEnd = before.length;
    hideDropdown();
  }

  function hideDropdown() {
    if (dropdown) dropdown.classList.add('hidden');
  }
}