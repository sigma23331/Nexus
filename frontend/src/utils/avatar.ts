// 旧的默认头像 URL
const OLD_DEFAULT_AVATAR = 'https://api.xinyundao.com/default_avatar.png'
// 新的默认头像本地路径
const NEW_DEFAULT_AVATAR = '/images/avatar.png'

/**
 * 获取有效的头像 URL
 * @param avatar - 用户存储的头像 URL
 * @returns 最终展示的头像 URL
 */
export function getValidAvatar(avatar?: string | null): string {
  if (!avatar || avatar === OLD_DEFAULT_AVATAR) {
    return NEW_DEFAULT_AVATAR
  }
  return avatar
}
