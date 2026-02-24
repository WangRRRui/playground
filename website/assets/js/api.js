/**
 * Blog API Client
 * Provides methods to interact with the backend API
 */

const BlogAPI = (function() {
    // API base URL - change in production
    const BASE_URL = '/api/v1';

    /**
     * Make an API request
     */
    async function request(endpoint, options = {}) {
        const url = `${BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            if (response.status === 204) return null;
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    return {
        /**
         * Get paginated list of posts
         * @param {Object} params - Query parameters
         * @param {number} params.page - Page number (default: 1)
         * @param {number} params.page_size - Items per page (default: 10)
         * @param {string} params.tag - Filter by tag name
         * @param {string} params.search - Search in title/content
         */
        async getPosts(params = {}) {
            const query = new URLSearchParams({
                page: params.page || 1,
                page_size: params.page_size || 10,
                published_only: true,
                ...params
            }).toString();
            return request(`/posts?${query}`);
        },

        /**
         * Get latest N posts
         * @param {number} limit - Number of posts (default: 3)
         */
        async getLatestPosts(limit = 3) {
            return request(`/posts/latest?limit=${limit}`);
        },

        /**
         * Get a single post by slug
         * @param {string} slug - Post slug
         */
        async getPost(slug) {
            return request(`/posts/${slug}`);
        },

        /**
         * Get all tags with post counts
         */
        async getTags() {
            return request('/tags');
        },

        /**
         * Get posts by tag
         * @param {string} tagName - Tag name
         * @param {number} page - Page number
         */
        async getPostsByTag(tagName, page = 1) {
            return this.getPosts({ tag: tagName, page });
        },

        /**
         * Search posts
         * @param {string} query - Search query
         * @param {number} page - Page number
         */
        async searchPosts(query, page = 1) {
            return this.getPosts({ search: query, page });
        },

        /**
         * Get about settings (social links etc.)
         */
        async getAbout() {
            return request('/settings/about');
        },

        /**
         * Load footer social links from about settings.
         * Expects footer links to have id: footer-github, footer-twitter, footer-email
         */
        async loadFooterSocials() {
            try {
                const about = await this.getAbout();
                const mapping = {
                    'footer-github': about.social_github,
                    'footer-twitter': about.social_twitter,
                    'footer-email': about.social_email ? `mailto:${about.social_email}` : null,
                };
                for (const [id, url] of Object.entries(mapping)) {
                    const el = document.getElementById(id);
                    if (!el) continue;
                    if (url) {
                        el.href = url;
                        el.target = '_blank';
                        el.rel = 'noopener noreferrer';
                    } else {
                        el.style.display = 'none';
                    }
                }
            } catch (e) {
                // silently ignore - footer links stay as-is
            }
        }
    };
})();

// Export for ES modules if supported
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BlogAPI;
}
