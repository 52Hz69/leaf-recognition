/**
 * 后端接口配置
 *
 * 开发时后端一般跑在本机（127.0.0.1:5000）。
 * 用真机调试时，手机和电脑要在同一局域网，并把地址改成电脑的局域网 IP，
 * 例如 http://192.168.1.10:5000 （Windows 下用 ipconfig 查看 IPv4 地址）。
 *
 * 两种修改方式：
 *   1. 直接改下面这一行；
 *   2. 不改代码，在开发者工具 Console 里执行：
 *        wx.setStorageSync('apiBaseUrl', 'http://192.168.1.10:5000')
 *      然后重新点击“开始识别”即可生效，清空用 wx.removeStorageSync('apiBaseUrl')。
 */
export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:5000'

export function getApiBaseUrl(): string {
  const custom = wx.getStorageSync('apiBaseUrl')
  const base = (custom && String(custom)) || DEFAULT_API_BASE_URL
  return base.replace(/\/+$/, '')
}
