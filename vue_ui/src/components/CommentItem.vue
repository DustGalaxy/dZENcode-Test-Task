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

const selectedText = ref<string | null>(null);
const isTextLoading = ref(false);

const openText = async (url: string) => {
  isTextLoading.value = true;
  selectedText.value = ""; // Clear previous
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to load text file");

    // Get blob to handle encoding
    const blob = await response.blob();
    const text = await blob.text(); // blob.text() automatically handles UTF-8
    selectedText.value = text;
  } catch (e) {
    console.error(e);
    selectedText.value = "Failed to load text content.";
  } finally {
    isTextLoading.value = false;
  }
};

const closeText = () => {
  selectedText.value = null;
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
          <!-- Image -->
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

          <!-- Text File -->
          <div
            v-else-if="attachment.file.toLowerCase().endsWith('.txt')"
            @click="openText(attachment.file)"
            class="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded text-sm text-indigo-600 dark:text-indigo-400 hover:bg-gray-200 dark:hover:bg-gray-600 cursor-pointer border border-gray-200 dark:border-gray-600 transition-colors"
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>View Text</span>
          </div>

          <!-- Other File -->
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
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
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

    <!-- Text Modal -->
    <div
      v-if="selectedText !== null || isTextLoading"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click="closeText"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] flex flex-col shadow-xl"
        @click.stop
      >
        <div
          class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700"
        >
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Text Content
          </h3>
          <button
            @click="closeText"
            class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <div class="p-4 overflow-auto flex-1">
          <div
            v-if="isTextLoading"
            class="flex justify-center items-center h-32"
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
          <pre
            v-else
            class="whitespace-pre-wrap font-mono text-sm text-gray-800 dark:text-gray-200"
            >{{ selectedText }}</pre
          >
        </div>
      </div>
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
