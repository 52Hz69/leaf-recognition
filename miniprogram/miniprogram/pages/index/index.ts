// pages/index/index.ts
import { getApiBaseUrl } from '../../utils/config'

interface Prediction {
  class_id: number
  raw_class: string
  class_name: string
  confidence: number
  confText: string
}

Page({
  data: {
    imagePath: '',
    predictions: [] as Prediction[],
    isProcessing: false,
    hasRecognized: false,
  },

  // 选择图片（相册或拍照）
  chooseImage() {
    const that = this
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success(res) {
        that.setData({
          imagePath: res.tempFiles[0].tempFilePath,
          predictions: [],
          hasRecognized: false,
        })
      },
      fail(err) {
        console.error('选择图片失败', err)
        wx.showToast({ title: '选择图片失败', icon: 'none' })
      },
    })
  },

  // 上传图片并识别
  recognizeImage() {
    const that = this
    if (!this.data.imagePath) {
      wx.showToast({ title: '请先选择图片', icon: 'none' })
      return
    }
    if (this.data.isProcessing) {
      return
    }

    this.setData({ isProcessing: true })
    wx.showLoading({ title: '识别中...', mask: true })

    wx.uploadFile({
      url: `${getApiBaseUrl()}/predict`,
      filePath: this.data.imagePath,
      name: 'file',
      formData: {
        confidence: 0.5,
      },
      success(uploadRes) {
        wx.hideLoading()
        that.setData({ isProcessing: false })

        try {
          const data = JSON.parse(uploadRes.data)
          const list: Prediction[] = data.predictions || data.detections || []

          if (data.success && list.length > 0) {
            const predictions = list.map((item: Prediction) => ({
              class_id: item.class_id,
              raw_class: item.raw_class,
              class_name: item.class_name,
              confidence: item.confidence,
              confText: `${(item.confidence * 100).toFixed(2)}%`,
            }))
            that.setData({ predictions, hasRecognized: true })
            wx.showToast({ title: `识别为：${predictions[0].class_name}`, icon: 'none' })
          } else {
            that.setData({ predictions: [], hasRecognized: true })
            wx.showToast({ title: data.error || '识别失败', icon: 'none' })
          }
        } catch (e) {
          console.error('响应解析失败', e)
          that.setData({ predictions: [], hasRecognized: true })
          wx.showToast({ title: '返回数据格式错误', icon: 'none' })
        }
      },
      fail(err) {
        wx.hideLoading()
        that.setData({ isProcessing: false })
        console.error('网络请求失败', err)
        wx.showToast({ title: '网络请求失败，请检查后端地址', icon: 'none' })
      },
    })
  },
})
