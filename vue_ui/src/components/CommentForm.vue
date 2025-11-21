<script setup lang="ts">
import { ref, onBeforeUnmount } from "vue";
import { useCommentsStore } from "../stores/commentsStore";
import { useAuthStore } from "../stores/authStore";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";

const props = defineProps<{
  replyTo?: number;
  onSuccess?: () => void;
}>();

const store = useCommentsStore();
const authStore = useAuthStore();
const error = ref("");
const previewHtml = ref("");
const showPreview = ref(false);
const isPreviewLoading = ref(false);

const editor = useEditor({
  content: "",
  extensions: [
    StarterKit,
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        class: "text-indigo-600 hover:underline",
      },
    }),
  ],
  editorProps: {
    attributes: {
      class:
        "prose dark:prose-invert max-w-none focus:outline-none min-h-[100px] p-3",
    },
  },
});

const setLink = () => {
  const previousUrl = editor.value?.getAttributes("link").href;
  const url = window.prompt("URL", previousUrl);

  // cancelled
  if (url === null) {
    return;
  }

  // empty
  if (url === "") {
    editor.value?.chain().focus().extendMarkRange("link").unsetLink().run();
    return;
  }

  // update
  editor.value
    ?.chain()
    .focus()
    .extendMarkRange("link")
    .setLink({ href: url })
    .run();
};

const fetchPreview = async () => {
  if (!editor.value || editor.value.isEmpty) return;

  isPreviewLoading.value = true;
  showPreview.value = true;
  try {
    const rawText = editor.value.getHTML();
    const response = await fetch(
      "http://127.0.0.1:8000/api/comments/preview-text/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authStore.accessToken}`,
        },
        body: JSON.stringify({ text: rawText }),
      }
    );

    if (!response.ok) throw new Error("Preview failed");

    const data = await response.json();
    previewHtml.value = data.text;
  } catch (e) {
    error.value = "Failed to load preview";
  } finally {
    isPreviewLoading.value = false;
  }
};

const handleSubmit = async () => {
  if (!editor.value || editor.value.isEmpty) {
    error.value = "Comment cannot be empty";
    return;
  }

  try {
    const content = editor.value.getHTML();
    await store.addComment(content, props.replyTo);
    editor.value.commands.clearContent();
    error.value = "";
    showPreview.value = false;
    previewHtml.value = "";
    if (props.onSuccess) {
      props.onSuccess();
    }
  } catch (e: any) {
    error.value = "Failed to post comment";
  }
};

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>

<template>
  <div
    class="text-white bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
  >
    <h3 class="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">
      {{ replyTo ? "Leave a Reply" : "Post a Comment" }}
    </h3>

    <div
      class="mb-2 bg-white dark:bg-gray-800 rounded-md border border-gray-300 dark:border-gray-600 overflow-hidden"
    >
      <!-- Toolbar -->
      <div
        v-if="editor"
        class="flex items-center gap-1 p-2 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
      >
        <button
          @click="editor.chain().focus().toggleBold().run()"
          :class="{ 'bg-gray-200 dark:bg-gray-700': editor.isActive('bold') }"
          class="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
          title="Bold"
        >
          <strong>B</strong>
        </button>
        <button
          @click="editor.chain().focus().toggleItalic().run()"
          :class="{ 'bg-gray-200 dark:bg-gray-700': editor.isActive('italic') }"
          class="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 italic"
          title="Italic"
        >
          I
        </button>
        <button
          @click="editor.chain().focus().toggleCode().run()"
          :class="{ 'bg-gray-200 dark:bg-gray-700': editor.isActive('code') }"
          class="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-mono text-xs"
          title="Code"
        >
          &lt;/&gt;
        </button>
        <button
          @click="setLink"
          :class="{ 'bg-gray-200 dark:bg-gray-700': editor.isActive('link') }"
          class="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 underline"
          title="Link"
        >
          Link
        </button>
      </div>

      <editor-content :editor="editor" />
    </div>

    <div v-if="error" class="text-red-500 text-sm mb-2">{{ error }}</div>

    <!-- Preview Area -->
    <div
      v-if="showPreview"
      class="mb-4 p-4 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700"
    >
      <h4 class="text-xs font-bold text-gray-500 uppercase mb-2">Preview</h4>
      <div v-if="isPreviewLoading" class="text-sm text-gray-500">
        Loading preview...
      </div>
      <div
        v-else
        class="preview-content max-w-none text-gray-900 dark:text-gray-100"
        v-html="previewHtml"
      ></div>
    </div>

    <div class="flex justify-end gap-2">
      <button
        @click="fetchPreview"
        type="button"
        class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded-md font-medium text-sm transition-colors"
      >
        Preview
      </button>

      <button
        @click="handleSubmit"
        :disabled="store.loading"
        class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md font-medium text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
      >
        <span v-if="store.loading" class="mr-2">
          <svg
            class="animate-spin h-4 w-4 text-white"
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
        </span>
        {{ replyTo ? "Reply" : "Post Comment" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.preview-content :deep(a) {
  color: #4f46e5; /* indigo-600 */
  background-color: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
  padding: 2px 4px;
  text-decoration: none;
}

.dark .preview-content :deep(a) {
  color: #818cf8; /* indigo-400 */
}

.preview-content :deep(a):hover {
  text-decoration: underline;
}
</style>
