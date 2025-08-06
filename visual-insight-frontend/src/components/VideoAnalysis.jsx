import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Play, Pause, SkipBack, SkipForward, Volume2, Maximize } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { useVideo } from '../contexts/VideoContext'

export default function VideoAnalysis() {
  const { id } = useParams()
  const { currentVideo, fetchVideo, fetchVideoEvents } = useVideo()
  const [events, setEvents] = useState([])
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [volume, setVolume] = useState(100)

  useEffect(() => {
    if (id) {
      fetchVideo(id)
      fetchVideoEvents(id).then(setEvents)
    }
  }, [id])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-500'
      case 'violation': return 'bg-red-400'
      case 'warning': return 'bg-orange-400'
      case 'info': return 'bg-blue-400'
      default: return 'bg-gray-400'
    }
  }

  if (!currentVideo) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {currentVideo.title}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {currentVideo.description || 'Video analysis and insights'}
            </p>
          </div>
          <Badge 
            variant={currentVideo.status === 'completed' ? 'default' : 'secondary'}
            className="text-sm"
          >
            {currentVideo.status}
          </Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Video Player */}
          <div className="lg:col-span-2">
            <Card className="border-0 shadow-lg">
              <CardContent className="p-0">
                <div className="relative bg-black rounded-t-lg aspect-video">
                  {/* Mock Video Player */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-white text-center">
                      <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mb-4 mx-auto">
                        <Play className="h-8 w-8 ml-1" />
                      </div>
                      <p className="text-sm opacity-75">Video Player</p>
                      <p className="text-xs opacity-50">Click to play</p>
                    </div>
                  </div>
                  
                  {/* Event Markers Overlay */}
                  <div className="absolute bottom-16 left-4 right-4">
                    <div className="relative h-2 bg-white/20 rounded-full">
                      {events.map((event, index) => (
                        <div
                          key={event.id || index}
                          className={`absolute top-0 w-1 h-2 rounded-full ${getSeverityColor(event.severity)}`}
                          style={{ left: `${(event.start_time / duration) * 100}%` }}
                          title={event.title}
                        />
                      ))}
                    </div>
                  </div>
                </div>
                
                {/* Video Controls */}
                <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-b-lg">
                  <div className="flex items-center space-x-4">
                    <Button variant="ghost" size="sm">
                      <SkipBack className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => setPlaying(!playing)}>
                      {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                    </Button>
                    <Button variant="ghost" size="sm">
                      <SkipForward className="h-4 w-4" />
                    </Button>
                    
                    <div className="flex-1 flex items-center space-x-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {formatTime(currentTime)}
                      </span>
                      <Slider
                        value={[currentTime]}
                        max={duration || 100}
                        step={1}
                        className="flex-1"
                        onValueChange={(value) => setCurrentTime(value[0])}
                      />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {formatTime(duration)}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Volume2 className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      <Slider
                        value={[volume]}
                        max={100}
                        step={1}
                        className="w-20"
                        onValueChange={(value) => setVolume(value[0])}
                      />
                    </div>
                    
                    <Button variant="ghost" size="sm">
                      <Maximize className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Events Panel */}
          <div>
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle>Detected Events</CardTitle>
                <CardDescription>
                  {events.length} events found in this video
                </CardDescription>
              </CardHeader>
              <CardContent className="max-h-96 overflow-y-auto">
                {events.length > 0 ? (
                  <div className="space-y-3">
                    {events.map((event, index) => (
                      <motion.div
                        key={event.id || index}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                        onClick={() => setCurrentTime(event.start_time)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <Badge 
                                variant={event.severity === 'violation' || event.severity === 'critical' ? 'destructive' : 'secondary'}
                                className="text-xs"
                              >
                                {event.severity}
                              </Badge>
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {formatTime(event.start_time)}
                              </span>
                            </div>
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                              {event.title}
                            </h4>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {event.description}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 dark:text-gray-400">No events detected</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Analysis Summary */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle>Analysis Summary</CardTitle>
            <CardDescription>Key insights and statistics from the video analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {events.length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Events</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {events.filter(e => e.is_violation).length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Violations</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {events.filter(e => e.severity === 'warning').length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Warnings</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {currentVideo.confidence_score || '92'}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Confidence</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

