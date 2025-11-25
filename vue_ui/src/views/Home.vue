<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useCommentsStore } from "../stores/commentsStore";
import CommentItem from "../components/CommentItem.vue";
import CommentForm from "../components/CommentForm.vue";
import { useAuthStore } from "../stores/authStore";

const store = useCommentsStore();
const authStore = useAuthStore();

const localSearch = ref("");
const localSort = ref("-created_at");

const totalPages = computed(() => Math.ceil(store.totalComments / 25));

const applyFilters = () => {
  store.fetchComments(1, localSort.value, localSearch.value);
};

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    store.fetchComments(page, localSort.value, localSearch.value);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

onMounted(() => {
  store.fetchComments();
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Comments Feed
      </h1>
      <button
        @click="store.fetchComments()"
        class="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
        title="Refresh"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      </button>
    </div>

    <!-- Filters and Sort -->
    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-8">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1">
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >Search User</label
          >
          <input
            v-model="localSearch"
            type="text"
            placeholder="Search by name or email..."
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm px-4 py-2 border"
            @keyup.enter="applyFilters"
          />
        </div>
        <div class="w-full md:w-48">
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >Sort By</label
          >
          <select
            v-model="localSort"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-sm px-4 py-2 border"
            @change="applyFilters"
          >
            <option value="-created_at">Newest First</option>
            <option value="created_at">Oldest First</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="applyFilters"
            class="w-full md:w-auto px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Apply
          </button>
        </div>
      </div>
    </div>

    <div class="mb-8" v-if="authStore.isAuthenticated">
      <CommentForm />
    </div>

    <div
      v-if="store.loading && store.comments.length === 0"
      class="flex justify-center py-12"
    >
      <svg
        class="animate-spin h-8 w-8 text-indigo-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </div>

    <div
      v-else-if="store.error"
      class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg text-red-600 dark:text-red-400 text-center mb-6"
    >
      {{ store.error }}
    </div>

    <div v-else class="space-y-4">
      <CommentItem
        v-for="comment in store.comments"
        :key="comment.id"
        :comment="comment"
      />

      <div
        v-if="store.comments && store.comments.length === 0"
        class="text-center py-12 text-gray-500 dark:text-gray-400"
      >
        No comments yet. Be the first to share your thoughts!
      </div>
    </div>

    <!-- Pagination -->
    <div
      v-if="totalPages > 0"
      class="mt-8 flex justify-between items-center space-x-4"
    >
      <button
        @click="changePage(store.currentPage - 1)"
        :disabled="store.currentPage === 1"
        class="w-24 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
      >
        Previous
      </button>
      <span class="text-sm text-gray-700 dark:text-gray-300">
        Page {{ store.currentPage }} of {{ totalPages }}
      </span>
      <button
        @click="changePage(store.currentPage + 1)"
        :disabled="store.currentPage === totalPages"
        class="w-24 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
      >
        Next
      </button>
    </div>
  </div>
</template>
