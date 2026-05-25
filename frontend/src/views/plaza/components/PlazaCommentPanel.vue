<template>
  <div class="border-t border-slate-100 px-4 py-3 bg-slate-50/60">
    <!-- 发表评论 -->
    <div class="flex gap-2 items-end">
      <textarea
        v-model="draft"
        :placeholder="replyTarget ? `回复 @${replyTarget.nickname}` : '写下你的评论…'"
        rows="2"
        maxlength="200"
        class="flex-1 resize-none rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-200"
        @keydown.enter.exact.prevent="submitDraft"
      />
      <button
        type="button"
        :disabled="submitting || !draft.trim()"
        class="shrink-0 rounded-xl bg-purple-600 px-3 py-2 text-xs font-medium text-white disabled:opacity-40"
        @click="submitDraft"
      >
        {{ submitting ? '发送中' : '发送' }}
      </button>
    </div>
    <p v-if="replyTarget" class="mt-1 text-xs text-slate-500">
      正在回复 @{{ replyTarget.nickname }}
      <button type="button" class="ml-2 text-purple-600" @click="cancelReply">取消</button>
    </p>
    <p class="mt-1 text-right text-[10px] text-slate-400">{{ draft.length }}/200</p>

    <p v-if="errorMsg" class="mt-2 text-xs text-rose-500">{{ errorMsg }}</p>

    <!-- 评论列表 -->
    <div v-if="loading" class="py-4 text-center text-xs text-slate-400">评论加载中…</div>
    <div v-else-if="comments.length === 0" class="py-4 text-center text-xs text-slate-400">
      还没有评论，来抢沙发吧～
    </div>
    <ul v-else class="mt-3 space-y-4">
      <li v-for="comment in comments" :key="comment.commentId" class="space-y-2">
        <CommentItem
          :comment="comment"
          :is-reply="false"
          @reply="startReply"
          @delete="handleDelete"
        />
        <!-- 回复预览 -->
        <ul v-if="comment.replies.length" class="ml-10 space-y-2 border-l border-slate-200 pl-3">
          <li v-for="reply in comment.replies" :key="reply.commentId">
            <CommentItem
              :comment="reply"
              :is-reply="true"
              @reply="startReply"
              @delete="handleDelete"
            />
          </li>
        </ul>
        <button
          v-if="comment.replyCount > comment.replies.length"
          type="button"
          class="ml-10 text-xs text-purple-600"
          :disabled="loadingRepliesId === comment.commentId"
          @click="loadAllReplies(comment)"
        >
          {{
            loadingRepliesId === comment.commentId
              ? '加载中…'
              : `查看全部 ${comment.replyCount} 条回复`
          }}
        </button>
      </li>
    </ul>

    <button
      v-if="hasMore && !loading"
      type="button"
      class="mt-3 w-full text-center text-xs text-purple-600"
      :disabled="loadingMore"
      @click="loadMoreComments"
    >
      {{ loadingMore ? '加载中…' : '加载更多评论' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import CommentItem from './PlazaCommentItem.vue'
import {
  createPlazaComment,
  deletePlazaComment,
  getPlazaCommentReplies,
  getPlazaComments,
} from '@/api/plaza'
import type { PlazaComment } from '@/types/models'

const props = defineProps<{
  cardId: string
  commentsCount: number
}>()

const emit = defineEmits<{
  (e: 'update:commentsCount', value: number): void
}>()

const comments = ref<PlazaComment[]>([])
const draft = ref('')
const loading = ref(false)
const loadingMore = ref(false)
const submitting = ref(false)
const hasMore = ref(false)
const nextCursor = ref<string | null>(null)
const errorMsg = ref('')
const replyTarget = ref<{ commentId: string; nickname: string } | null>(null)
const loadingRepliesId = ref<string | null>(null)

const fetchComments = async (reset = true) => {
  if (reset) {
    loading.value = true
    nextCursor.value = null
  } else {
    loadingMore.value = true
  }
  errorMsg.value = ''
  try {
    const res = await getPlazaComments(props.cardId, {
      cursor: reset ? null : nextCursor.value,
      limit: 20,
    })
    if (reset) {
      comments.value = res.list
    } else {
      comments.value.push(...res.list)
    }
    nextCursor.value = res.nextCursor
    hasMore.value = res.hasMore
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '加载评论失败'
    if (reset) comments.value = []
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const loadMoreComments = () => {
  if (!hasMore.value || loadingMore.value) return
  fetchComments(false)
}

const startReply = (comment: PlazaComment) => {
  const parentId = comment.parentId || comment.commentId
  replyTarget.value = {
    commentId: parentId,
    nickname: comment.owner.nickname,
  }
}

const cancelReply = () => {
  replyTarget.value = null
}

const submitDraft = async () => {
  const text = draft.value.trim()
  if (!text || submitting.value) return
  submitting.value = true
  errorMsg.value = ''
  try {
    const created = await createPlazaComment(props.cardId, {
      content: text,
      ...(replyTarget.value ? { parentId: replyTarget.value.commentId } : {}),
    })
    draft.value = ''
    replyTarget.value = null

    if (created.parentId) {
      const parent = comments.value.find((c) => c.commentId === created.parentId)
      if (parent) {
        parent.replies = [...parent.replies, created]
        parent.replyCount += 1
      }
    } else {
      comments.value = [created, ...comments.value]
    }

    if (created.status === 'visible') {
      emit('update:commentsCount', props.commentsCount + 1)
    }
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '发送失败'
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (comment: PlazaComment) => {
  if (!confirm('确定删除这条评论吗？')) return
  try {
    await deletePlazaComment(comment.commentId)
    if (comment.parentId) {
      const parent = comments.value.find((c) => c.commentId === comment.parentId)
      if (parent) {
        parent.replies = parent.replies.filter((r) => r.commentId !== comment.commentId)
        parent.replyCount = Math.max(0, parent.replyCount - 1)
      }
    } else {
      comments.value = comments.value.filter((c) => c.commentId !== comment.commentId)
    }
    emit('update:commentsCount', Math.max(0, props.commentsCount - 1))
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '删除失败'
  }
}

const loadAllReplies = async (comment: PlazaComment) => {
  loadingRepliesId.value = comment.commentId
  try {
    const res = await getPlazaCommentReplies(comment.commentId, { limit: 20 })
    const idx = comments.value.findIndex((c) => c.commentId === comment.commentId)
    if (idx !== -1) {
      comments.value[idx] = { ...comments.value[idx], replies: res.list }
    }
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '加载回复失败'
  } finally {
    loadingRepliesId.value = null
  }
}

watch(
  () => props.cardId,
  () => {
    fetchComments(true)
  },
  { immediate: true },
)
</script>
