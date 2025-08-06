import { createContext, useContext, useState, useEffect } from 'react'
import { useAuth } from './AuthContext'

const VideoContext = createContext()

export function useVideo() {
  const context = useContext(VideoContext)
  if (!context) {
    throw new Error('useVideo must be used within a VideoProvider')
  }
  return context
}

export function VideoProvider({ children }) {
  const { token, API_BASE_URL } = useAuth()
  const [videos, setVideos] = useState([])
  const [currentVideo, setCurrentVideo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const fetchVideos = async () => {
    if (!token) return

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/videos/`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setVideos(data.results || data)
      }
    } catch (error) {
      console.error('Error fetching videos:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchVideo = async (videoId) => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentVideo(data)
        return data
      }
    } catch (error) {
      console.error('Error fetching video:', error)
    }
  }

  const uploadVideo = async (formData, onProgress) => {
    if (!token) return

    try {
      const xhr = new XMLHttpRequest()
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const progress = Math.round((e.loaded / e.total) * 100)
            setUploadProgress(progress)
            if (onProgress) onProgress(progress)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status === 201) {
            const data = JSON.parse(xhr.responseText)
            setVideos(prev => [data.video, ...prev])
            setUploadProgress(0)
            resolve({ success: true, data: data.video })
          } else {
            reject({ success: false, error: 'Upload failed' })
          }
        })

        xhr.addEventListener('error', () => {
          setUploadProgress(0)
          reject({ success: false, error: 'Network error' })
        })

        xhr.open('POST', `${API_BASE_URL}/videos/upload/`)
        xhr.setRequestHeader('Authorization', `Token ${token}`)
        xhr.send(formData)
      })
    } catch (error) {
      console.error('Upload error:', error)
      setUploadProgress(0)
      return { success: false, error: 'Upload failed' }
    }
  }

  const startAnalysis = async (videoId, analysisConfig) => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/analyze/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisConfig),
      })

      const data = await response.json()

      if (response.ok) {
        // Update video status
        setVideos(prev => prev.map(video => 
          video.id === videoId 
            ? { ...video, status: 'processing' }
            : video
        ))
        return { success: true, data }
      } else {
        return { success: false, error: data.error || 'Analysis failed to start' }
      }
    } catch (error) {
      console.error('Analysis start error:', error)
      return { success: false, error: 'Network error. Please try again.' }
    }
  }

  const getAnalysisStatus = async (videoId) => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/status/`, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        
        // Update video in list
        setVideos(prev => prev.map(video => 
          video.id === videoId 
            ? { ...video, status: data.status }
            : video
        ))
        
        return data
      }
    } catch (error) {
      console.error('Error fetching analysis status:', error)
    }
  }

  const fetchVideoEvents = async (videoId, filters = {}) => {
    if (!token) return

    try {
      const queryParams = new URLSearchParams(filters).toString()
      const url = `${API_BASE_URL}/videos/${videoId}/events/${queryParams ? `?${queryParams}` : ''}`
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        return data.results || data
      }
    } catch (error) {
      console.error('Error fetching video events:', error)
    }
  }

  const deleteVideo = async (videoId) => {
    if (!token) return

    try {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        setVideos(prev => prev.filter(video => video.id !== videoId))
        if (currentVideo?.id === videoId) {
          setCurrentVideo(null)
        }
        return { success: true }
      } else {
        return { success: false, error: 'Delete failed' }
      }
    } catch (error) {
      console.error('Delete error:', error)
      return { success: false, error: 'Network error. Please try again.' }
    }
  }

  useEffect(() => {
    if (token) {
      fetchVideos()
    }
  }, [token])

  const value = {
    videos,
    currentVideo,
    loading,
    uploadProgress,
    fetchVideos,
    fetchVideo,
    uploadVideo,
    startAnalysis,
    getAnalysisStatus,
    fetchVideoEvents,
    deleteVideo,
    setCurrentVideo,
  }

  return (
    <VideoContext.Provider value={value}>
      {children}
    </VideoContext.Provider>
  )
}

