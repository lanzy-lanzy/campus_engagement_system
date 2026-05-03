// Custom JavaScript for PulseCampus
window.mentionComposer = function(initialValue) {
  return {
    activeIndex: 0,
    editor: null,
    friends: [],
    hidden: null,
    lookupId: 0,
    open: false,
    value: initialValue || '',

    init(editor, hidden) {
      this.editor = editor;
      this.hidden = hidden;
      this.value = initialValue || hidden.value || '';
      this.render(this.value.length);
      this.syncHidden();
    },

    initialFor(friend) {
      return String((friend.display_name || friend.username || '?').charAt(0)).toUpperCase();
    },

    onInput() {
      const caret = this.getCaretOffset();
      this.value = this.editor.textContent || '';
      this.syncHidden();
      this.render(caret);
      this.updateSuggestions(caret);
    },

    onKeydown(event) {
      if (!this.open) return;

      if (event.key === 'ArrowDown') {
        event.preventDefault();
        this.activeIndex = this.friends.length ? (this.activeIndex + 1) % this.friends.length : 0;
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        this.activeIndex = this.friends.length ? (this.activeIndex <= 0 ? this.friends.length - 1 : this.activeIndex - 1) : 0;
      } else if (event.key === 'Enter' || event.key === 'Tab') {
        event.preventDefault();
        this.selectFriend(this.activeIndex);
      } else if (event.key === 'Escape') {
        this.open = false;
      }
    },

    onBlur() {
      window.setTimeout(() => {
        this.open = false;
      }, 120);
    },

    selectFriend(index) {
      const friend = this.friends[index];
      if (!friend) return;

      const caret = this.getCaretOffset();
      const before = this.value.slice(0, caret).replace(/@[A-Za-z0-9_]*$/, `@${friend.username} `);
      const after = this.value.slice(caret);
      this.value = before + after;
      this.syncHidden();
      this.open = false;
      this.render(before.length);
      this.editor.focus();
    },

    updateSuggestions(caret) {
      const match = this.value.slice(0, caret).match(/@([A-Za-z0-9_]*)$/);
      if (!match) {
        this.open = false;
        return;
      }

      const query = match[1];
      const lookupId = ++this.lookupId;
      fetch(`/accounts/friends/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
          if (lookupId !== this.lookupId) return;
          this.friends = data;
          this.activeIndex = 0;
          this.open = this.friends.length > 0;
        })
        .catch(() => {
          this.open = false;
        });
    },

    syncHidden() {
      if (this.hidden) {
        this.hidden.value = this.value;
      }
    },

    render(caretOffset) {
      if (!this.editor) return;
      this.editor.innerHTML = this.highlightMentions(this.value);
      this.setCaretOffset(Math.min(caretOffset, this.value.length));
    },

    highlightMentions(text) {
      return this.escapeHtml(text).replace(/(^|[^\w@])(@[A-Za-z0-9_]+)/g, '$1<span class="cv-mention">$2</span>');
    },

    escapeHtml(text) {
      return String(text || '').replace(/[&<>"']/g, function(ch) {
        return ({
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#39;'
        })[ch];
      });
    },

    getCaretOffset() {
      const selection = window.getSelection();
      if (!selection || selection.rangeCount === 0 || !this.editor.contains(selection.anchorNode)) {
        return this.value.length;
      }
      const range = selection.getRangeAt(0);
      const prefix = range.cloneRange();
      prefix.selectNodeContents(this.editor);
      prefix.setEnd(range.endContainer, range.endOffset);
      return prefix.toString().length;
    },

    setCaretOffset(offset) {
      const selection = window.getSelection();
      if (!selection || !this.editor) return;

      const range = document.createRange();
      let remaining = offset;
      const walker = document.createTreeWalker(this.editor, NodeFilter.SHOW_TEXT);
      let node = walker.nextNode();

      while (node) {
        const length = node.nodeValue.length;
        if (remaining <= length) {
          range.setStart(node, remaining);
          range.collapse(true);
          selection.removeAllRanges();
          selection.addRange(range);
          return;
        }
        remaining -= length;
        node = walker.nextNode();
      }

      range.selectNodeContents(this.editor);
      range.collapse(false);
      selection.removeAllRanges();
      selection.addRange(range);
    }
  };
};

window.pulseDefaultReaction = function(button) {
  if (!button || !window.htmx) return;
  const hasReaction = Boolean(button.dataset.currentReactionKind);
  const url = hasReaction ? button.dataset.defaultReactionUrl : button.dataset.quickReactionUrl;
  const target = button.dataset.reactionTarget;
  if (!url || !target) return;

  htmx.ajax('POST', url, {
    target: target,
    swap: 'outerHTML',
    source: button
  });
};

window.previewPostReaction = function(el) {
  try {
    if (!el) return;
    const kind = el.dataset.kind || '';
    const iconHtml = el.innerHTML || el.dataset.icon || '';

    // Find containing post stats block (feed or modal)
    let container = el.closest('[id^="post-stats-"]');
    if (!container) container = el.closest('[id^="modal-post-stats-"]');
    // Fallback to hx-target selector
    if (!container) {
      const target = el.getAttribute('hx-target');
      if (target) container = document.querySelector(target);
    }
    if (!container) return;

    // Update current reaction data attribute
    try { container.dataset.currentReaction = kind; } catch (e) {}

    // Update inline like icon
    const inline = container.querySelector('.cv-fb-inline-like');
    if (inline) {
      inline.classList.add('active');
      inline.innerHTML = iconHtml;
    }

    // Mark the main toggle button as active and update ARIA
    const mainBtn = container.querySelector('button[aria-pressed]');
    if (mainBtn) {
      mainBtn.classList.add('active');
      mainBtn.setAttribute('aria-pressed', 'true');
      mainBtn.setAttribute('aria-label', `Remove ${kind} reaction`);
    }

    // Update active state inside the picker
    const prevActive = container.querySelector('.cv-fb-reaction-option.active');
    if (prevActive) prevActive.classList.remove('active');
    try { el.classList.add('active'); } catch (e) {}
  } catch (e) {
    console.warn('previewPostReaction failed', e);
  }
};

document.addEventListener('DOMContentLoaded', function() {
  initPulseScenes();
  initMentions();
  initChatInput();
});

function initMentions() {
  if (window.htmx) {
    htmx.config.defaultSwapStyle = 'outerHTML';

    document.body.addEventListener('htmx:configRequest', function(evt) {
      const csrfMatch = document.cookie.match(/csrftoken=([^;]+)/);
      if (csrfMatch) {
        evt.detail.headers['X-CSRFToken'] = csrfMatch[1];
      }
    });
  }

  // Mentions - run on DOMContentLoaded
  const fields = document.querySelectorAll('[data-mentions]');
  fields.forEach(initMentionField);

  // Also run on HTMX swap for dynamically loaded content
  document.body.addEventListener('htmx:afterSwap', function(evt) {
    document.querySelectorAll('[data-mentions]').forEach(initMentionField);
    initChatInput();
    // Initialize Alpine.js for newly swapped-in fragments so x-data/x-show work
    try {
      if (window.Alpine && evt && evt.detail && evt.detail.target) {
        Alpine.initTree(evt.detail.target);
      }
    } catch (e) {
      console.warn('Alpine initTree failed on HTMX swap', e);
    }
  });
}

function initMentionField(textarea) {
  if (textarea.dataset.mentionInit) return;
  textarea.dataset.mentionInit = 'true';

  let dropdown = null;
  let friends = [];
  let activeIndex = 0;

  textarea.addEventListener('input', handleInput);
  textarea.addEventListener('keydown', handleKeydown);
  textarea.addEventListener('blur', function() {
    window.setTimeout(hideDropdown, 120);
  });

  function handleInput(e) {
    const pos = textarea.selectionStart;
    const text = textarea.value;
    const before = text.slice(0, pos);
    const match = before.match(/@([A-Za-z0-9_]*)$/);
    
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
      } else if (e.key === 'Tab') {
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
        activeIndex = 0;
        if (friends.length === 0) {
          hideDropdown();
          return;
        }
        if (!dropdown) {
          dropdown = document.createElement('div');
          dropdown.className = 'mention-dropdown hidden';
          const wrapper = textarea.parentNode;
          if (window.getComputedStyle(wrapper).position === 'static') {
            wrapper.style.position = 'relative';
          }
          wrapper.appendChild(dropdown);
        }
        renderList();
        dropdown.classList.remove('hidden');
      })
      .catch(hideDropdown);
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, function(ch) {
      return ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      })[ch];
    });
  }

  function renderList() {
    const q = (textarea.value.slice(0, textarea.selectionStart).match(/@([A-Za-z0-9_]*)$/) || ['', ''])[1].toLowerCase();
    dropdown.innerHTML = friends.map((f, i) => {
      const username = escapeHtml(f.username);
      const displayName = escapeHtml(f.display_name || f.username);
      const department = escapeHtml(f.department || '');
      const initial = escapeHtml((f.display_name || f.username || '?').charAt(0).toUpperCase());
      const meta = department ? `<span class="mention-item-meta">${department}</span>` : `<span class="mention-item-meta">@${username}</span>`;
      const avatar = f.avatar_url
        ? `<img src="${escapeHtml(f.avatar_url)}" alt="">`
        : initial;
      const activeClass = i === activeIndex ? ' is-active' : '';

      return `<div class="mention-item${activeClass}" data-index="${i}">
        <div class="mention-item-avatar">${avatar}</div>
        <div class="min-w-0">
          <span class="mention-item-name">${displayName}</span>
          ${meta}
        </div>
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
    if (!items.length) return;
    activeIndex = (activeIndex + 1) % items.length;
    renderList();
  }

  function navigateUp() {
    const items = dropdown.querySelectorAll('.mention-item');
    if (!items.length) return;
    activeIndex = activeIndex <= 0 ? items.length - 1 : activeIndex - 1;
    renderList();
  }

  function selectCurrent() {
    selectFriend(activeIndex);
  }

  function selectFriend(idx) {
    const friend = friends[idx];
    if (!friend) return;
    const pos = textarea.selectionStart;
    const text = textarea.value;
    const before = text.slice(0, pos).replace(/@[A-Za-z0-9_]*$/, `@${friend.username} `);
    const after = text.slice(pos);
    textarea.value = before + after;
    textarea.selectionStart = textarea.selectionEnd = before.length;
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    hideDropdown();
  }

  function hideDropdown() {
    if (dropdown) dropdown.classList.add('hidden');
  }
}

function initPulseScenes() {
  const mounts = document.querySelectorAll('[data-pulse-scene]');
  if (!mounts.length || !window.THREE) return;

  mounts.forEach((mount) => {
    if (mount.dataset.pulseSceneReady) return;
    mount.dataset.pulseSceneReady = 'true';

    const THREE = window.THREE;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(0, 0, 8);

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch (error) {
      mount.classList.add('pc-scene-fallback');
      return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    const palette = [0x2c3e94, 0x5dade2, 0xa9dfbf, 0xff7a59];
    const positions = [
      [-2.8, 1.5, .1],
      [-1.1, -.4, .8],
      [.7, 1.1, -.4],
      [2.4, -.8, .4],
      [1.4, -2.0, -.2],
      [-2.1, -1.7, .2],
    ];

    const linePoints = [];
    positions.forEach((position, index) => {
      const geometry = new THREE.SphereGeometry(index % 2 ? .12 : .16, 24, 24);
      const material = new THREE.MeshStandardMaterial({
        color: palette[index % palette.length],
        roughness: .34,
        metalness: .08,
      });
      const node = new THREE.Mesh(geometry, material);
      node.position.set(position[0], position[1], position[2]);
      group.add(node);
      linePoints.push(new THREE.Vector3(position[0], position[1], position[2]));

      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(.32 + index * .025, .012, 12, 56),
        new THREE.MeshBasicMaterial({ color: palette[index % palette.length], transparent: true, opacity: .22 })
      );
      ring.position.copy(node.position);
      ring.rotation.x = Math.PI / 2.4;
      group.add(ring);
    });

    const lineGeometry = new THREE.BufferGeometry().setFromPoints(linePoints);
    const line = new THREE.Line(
      lineGeometry,
      new THREE.LineBasicMaterial({ color: 0x2c3e94, transparent: true, opacity: .28 })
    );
    group.add(line);

    const cardMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .42, metalness: .02 });
    const accentMaterial = new THREE.MeshStandardMaterial({ color: 0xff7a59, roughness: .3 });
    const cardPositions = [
      [-1.8, .4, -.2, -.12],
      [1.4, .55, .35, .14],
      [.15, -1.15, .15, -.04],
    ];
    cardPositions.forEach((item) => {
      const card = new THREE.Mesh(new THREE.BoxGeometry(1.65, .8, .08), cardMaterial);
      card.position.set(item[0], item[1], item[2]);
      card.rotation.z = item[3];
      group.add(card);

      const accent = new THREE.Mesh(new THREE.BoxGeometry(.5, .08, .1), accentMaterial);
      accent.position.set(item[0] - .42, item[1] + .18, item[2] + .07);
      accent.rotation.z = item[3];
      group.add(accent);
    });

    const ambient = new THREE.AmbientLight(0xffffff, 1.8);
    scene.add(ambient);
    const key = new THREE.DirectionalLight(0xffffff, 1.6);
    key.position.set(3, 4, 5);
    scene.add(key);

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const variant = mount.dataset.sceneVariant || 'landing';
    if (variant === 'auth') {
      group.scale.set(.88, .88, .88);
      group.position.y = -.35;
    }

    function resize() {
      const rect = mount.getBoundingClientRect();
      const width = Math.max(280, Math.floor(rect.width || mount.clientWidth || 640));
      const height = Math.max(260, Math.floor(rect.height || mount.clientHeight || 420));
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    }

    let frameId = 0;
    function render(time) {
      const t = time * 0.001;
      group.rotation.y = Math.sin(t * .45) * .16;
      group.rotation.x = Math.sin(t * .28) * .06;
      group.children.forEach((child, index) => {
        if (child.geometry && child.geometry.type === 'TorusGeometry') {
          child.scale.setScalar(1 + Math.sin(t * 1.4 + index) * .08);
        }
      });
      renderer.render(scene, camera);
      if (!prefersReducedMotion) {
        frameId = window.requestAnimationFrame(render);
      }
    }

    resize();
    window.addEventListener('resize', resize);
    render(0);

    if (prefersReducedMotion) {
      window.cancelAnimationFrame(frameId);
    }
  });
}

function initChatInput() {
  const composer = document.getElementById('chat-composer');
  if (!composer) return;

  const input = composer.querySelector('textarea[name="body"], input[name="body"]');
  if (!input) return;

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      if (e.shiftKey) {
        return;
      } else {
        e.preventDefault();
        composer.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      }
    }
  });
}
