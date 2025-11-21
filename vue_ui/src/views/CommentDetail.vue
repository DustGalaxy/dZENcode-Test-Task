<script setup lang="ts">
import { onMounted, onUnmounted, computed } from "vue";
import { useRoute } from "vue-router";
import { useCommentsStore } from "../stores/commentsStore";
import CommentItem from "../components/CommentItem.vue";

const route = useRoute();
const store = useCommentsStore();
const commentId = computed(() => Number(route.params.id));

onMounted(() => {
  store.fetchCommentDetail(commentId.value);
  store.connectWebSocket(commentId.value);
});

onUnmounted(() => {
  store.disconnectWebSocket();
});
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div
      v-if="store.loading && !store.currentComment"
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
      class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg text-red-600 dark:text-red-400 text-center"
    >
      {{ store.error }}
    </div>

    <div v-else-if="store.currentComment">
      <div class="mb-6">
        <router-link
          to="/"
          class="text-indigo-600 dark:text-indigo-400 hover:underline flex items-center mb-4"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          Back to Comments
        </router-link>

        <CommentItem :comment="store.currentComment" :is-detail="true" />
      </div>
    </div>
  </div>
</template>
