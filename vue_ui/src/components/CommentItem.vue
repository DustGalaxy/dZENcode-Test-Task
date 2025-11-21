<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import type { Comment } from "../stores/commentsStore";
import { useAuthStore } from "../stores/authStore";
import CommentForm from "./CommentForm.vue";

interface Props {
  comment: Comment;
  isDetail?: boolean;
}

const props = defineProps<Props>();

const router = useRouter();
const authStore = useAuthStore();
const showReplyForm = ref(false);

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString();
};

const goToDetail = () => {
  if (!props.isDetail) {
    router.push(`/comments/${props.comment.id}`);
  }
};

const toggleReplyForm = () => {
  showReplyForm.value = !showReplyForm.value;
};

const handleReplySuccess = () => {
  showReplyForm.value = false;
};
</script>

<template>
  <div class="flex flex-col gap-4">
    <div
      class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 transition-all hover:shadow-lg"
      :class="{ 'cursor-pointer': !isDetail }"
      @click="goToDetail"
    >
      <div class="flex justify-between items-start mb-2">
        <div class="flex items-center gap-2">
          <div
            class="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold"
          >
            {{ comment.user.username.charAt(0).toUpperCase() }}
          </div>
          <div>
            <h3 class="font-semibold text-gray-900 dark:text-gray-100">
              {{ comment.user.username }}
            </h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ comment.user.email }}
            </p>
          </div>
        </div>
        <span class="text-xs text-gray-400">{{
          formatDate(comment.created_at)
        }}</span>
      </div>

      <div
        class="prose dark:prose-invert max-w-none mb-3 text-white comment-content"
        v-html="comment.text"
      ></div>

      <div class="flex items-center justify-between mt-2">
        <div
          v-if="!isDetail"
          class="flex items-center text-sm text-indigo-600 dark:text-indigo-400 font-medium"
        >
          <span>View Replies</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 ml-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>

        <button
          v-if="isDetail && authStore.isAuthenticated"
          @click.stop="toggleReplyForm"
          class="text-sm text-indigo-600 dark:text-indigo-400 hover:underline focus:outline-none"
        >
          {{ showReplyForm ? "Cancel Reply" : "Reply" }}
        </button>
      </div>

      <!-- Reply Form -->
      <div v-if="showReplyForm" class="mt-4" @click.stop>
        <CommentForm :reply-to="comment.id" :on-success="handleReplySuccess" />
      </div>
    </div>

    <!-- Nested Replies -->
    <div
      v-if="isDetail && comment.replies && comment.replies.length > 0"
      class="pl-4 border-l-2 border-gray-200 dark:border-gray-700 ml-4 space-y-4"
    >
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :is-detail="true"
      />
    </div>
  </div>
</template>

<style scoped>
.comment-content :deep(a) {
  color: #4f46e5; /* indigo-600 */
  background-color: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  padding: 2px 4px;
  text-decoration: none;
}

.dark .comment-content :deep(a) {
  color: #818cf8; /* indigo-400 */
}

.comment-content :deep(a):hover {
  text-decoration: underline;
}
</style>
