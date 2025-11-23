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

const selectedImage = ref<string | null>(null);

const openImage = (url: string) => {
  selectedImage.value = url;
};

const closeImage = () => {
  selectedImage.value = null;
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

      <!-- Attachments -->
      <div
        v-if="comment.attachments && comment.attachments.length > 0"
        class="mt-2 mb-3 flex flex-wrap gap-2"
        @click.stop
      >
        <div v-for="attachment in comment.attachments" :key="attachment.id">
          <div
            v-if="attachment.media_type === 'image'"
            @click="openImage(attachment.file)"
            class="block w-24 h-24 rounded overflow-hidden border border-gray-200 dark:border-gray-700 hover:opacity-90 transition-opacity cursor-pointer"
          >
            <img
              :src="attachment.file"
              class="w-full h-full object-cover"
              alt="Attachment"
            />
          </div>
          <a
            v-else
            :href="attachment.file"
            target="_blank"
            class="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded text-sm text-indigo-600 dark:text-indigo-400 hover:underline border border-gray-200 dark:border-gray-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>Download File</span>
          </a>
        </div>
      </div>

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

    <!-- Image Modal -->
    <div
      v-if="selectedImage"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90 p-4"
      @click="closeImage"
    >
      <button
        @click="closeImage"
        class="absolute top-4 right-4 text-white hover:text-gray-300"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
      <img
        :src="selectedImage"
        class="max-w-full max-h-full object-contain"
        @click.stop
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
