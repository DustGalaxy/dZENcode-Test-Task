<script setup lang="ts">
import { ref, onBeforeUnmount } from "vue";
import { useCommentsStore } from "../stores/commentsStore";
import { useAuthStore } from "../stores/authStore";
import { commentsApi } from "../api/comments";
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
const files = ref<File[]>([]);
const fileInput = ref<HTMLInputElement | null>(null);

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

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    const newFiles = Array.from(target.files);
    const allowedTypes = ["text/plain", "image/jpeg", "image/png", "image/gif"];

    const validFiles = newFiles.filter((file) => {
      const isSizeValid = file.name.endsWith(".txt")
        ? file.size <= 100 * 1024
        : file.size <= 5 * 1024 * 1024;
      const isTypeValid =
        allowedTypes.includes(file.type) || file.name.endsWith(".txt");
      return isSizeValid && isTypeValid;
    });

    if (validFiles.length !== newFiles.length) {
      alert(
        "Some files were skipped. Max TXT size: 100KB. Max JPG, PNG, GIF size: 5MB. Allowed types: TXT, JPG, PNG, GIF."
      );
    }

    if (files.value.length + validFiles.length > 5) {
      alert("You can only attach up to 5 files.");
      return;
    }

    files.value = [...files.value, ...validFiles];
  }
  if (target.value) target.value = "";
};

const getFilePreview = (file: File) => {
  if (file.type.startsWith("image/")) {
    return URL.createObjectURL(file);
  }
  return null;
};

const removeFile = (index: number) => {
  files.value.splice(index, 1);
};

const fetchPreview = async () => {
  if (!editor.value || editor.value.isEmpty) return;

  isPreviewLoading.value = true;
  showPreview.value = true;
  try {
    const rawText = editor.value.getHTML();
    const data = await commentsApi.preview(rawText);
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
    await store.addComment(content, props.replyTo, files.value);
    editor.value.commands.clearContent();
    files.value = [];
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
      {{
        replyTo
          ? "Leave a Reply as - " + authStore.user?.username
          : "Post a Comment as - " + authStore.user?.username
      }}
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
        <div class="w-px h-4 bg-gray-300 dark:bg-gray-600 mx-1"></div>
        <button
          @click="triggerFileInput"
          class="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
          title="Attach File"
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
              d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
            />
          </svg>
        </button>

        <input
          type="file"
          ref="fileInput"
          multiple
          class="hidden"
          accept="image/jpeg, image/png, image/gif, .txt"
          @change="handleFileChange"
        />
      </div>

      <editor-content :editor="editor" />

      <!-- Selected Files -->
      <div
        v-if="files.length > 0"
        class="p-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex flex-wrap gap-2"
      >
        <div v-for="(file, index) in files" :key="index" class="relative group">
          <div
            v-if="getFilePreview(file)"
            class="w-16 h-16 rounded overflow-hidden border border-gray-300 dark:border-gray-600"
          >
            <img
              :src="getFilePreview(file)!"
              class="w-full h-full object-cover"
            />
          </div>
          <div
            v-else
            class="w-16 h-16 rounded border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xs text-gray-500 text-center p-1 break-all"
          >
            {{ file.name.split(".").pop() }}
          </div>

          <button
            @click="removeFile(index)"
            class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-0.5 shadow-sm hover:bg-red-600"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-3 w-3"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
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
