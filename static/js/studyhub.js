/* StudyHub — Alpine.js helpers & AJAX */

document.addEventListener('alpine:init', () => {
  Alpine.data('searchBox', () => ({
    query: '',
    suggestions: [],
    showSuggestions: false,
    loading: false,
    debounceTimer: null,

    search() {
      clearTimeout(this.debounceTimer);
      if (this.query.length < 2) {
        this.suggestions = [];
        return;
      }
      this.debounceTimer = setTimeout(async () => {
        this.loading = true;
        try {
          const res = await fetch(`/materials/api/suggestions/?q=${encodeURIComponent(this.query)}`);
          const data = await res.json();
          this.suggestions = data.suggestions || [];
          this.showSuggestions = true;
        } catch (e) {
          this.suggestions = [];
        }
        this.loading = false;
      }, 300);
    },

    hideSuggestions() {
      setTimeout(() => { this.showSuggestions = false; }, 200);
    },
  }));

  Alpine.data('toast', () => ({
    messages: [],
    show(msg, type = 'success') {
      const id = Date.now();
      this.messages.push({ id, msg, type });
      setTimeout(() => {
        this.messages = this.messages.filter(m => m.id !== id);
      }, 4000);
    },
  }));

  Alpine.data('infiniteScroll', (loadUrl) => ({
    page: 1,
    loading: false,
    hasMore: true,

    async loadMore() {
      if (this.loading || !this.hasMore) return;
      this.loading = true;
      this.page++;
      const params = new URLSearchParams(window.location.search);
      params.set('page', this.page);
      try {
        const res = await fetch(`${loadUrl}?${params}`, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const html = await res.text();
        if (!html.trim()) {
          this.hasMore = false;
        } else {
          document.getElementById('material-grid')?.insertAdjacentHTML('beforeend', html);
        }
      } catch (e) {
        this.hasMore = false;
      }
      this.loading = false;
    },

    init() {
      window.addEventListener('scroll', () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 400) {
          this.loadMore();
        }
      });
    },
  }));

  Alpine.data('fileDrop', () => ({
    dragOver: false,
    fileName: '',

    handleDrop(e, inputId) {
      e.preventDefault();
      this.dragOver = false;
      const files = e.dataTransfer.files;
      if (!files.length) return;
      const input = document.getElementById(inputId);
      if (!input) return;
      // Assign dropped file so it is included in form POST (modern browsers)
      const dt = new DataTransfer();
      dt.items.add(files[0]);
      input.files = dt.files;
      this.fileName = files[0].name;
    },

    handleSelect(e) {
      if (e.target.files.length) {
        this.fileName = e.target.files[0].name;
      }
    },
  }));

  Alpine.data('themeToggle', () => ({
    async toggle() {
      try {
        const res = await fetch('/dashboard/theme/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': document.querySelector('input[name=csrfmiddlewaretoken]')?.value ||
              document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '',
            'X-Requested-With': 'XMLHttpRequest',
          },
        });
        const data = await res.json();
        document.documentElement.setAttribute('data-theme', data.theme);
        localStorage.setItem('theme', data.theme);
      } catch (e) {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
      }
    },
  }));
});

// Apply saved theme on load
(function () {
  const theme = localStorage.getItem('theme') ||
    (document.documentElement.getAttribute('data-theme') || 'dark');
  document.documentElement.setAttribute('data-theme', theme);
})();
