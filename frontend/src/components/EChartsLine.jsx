import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const LINE_COLOR = '#0f766e'

export default function EChartsLine({ data, height = 280 }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current || !data?.length) return

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current)
    }

    const sample = data.slice(0, 200)
    const xData = sample.map((_, i) => i + 1)
    const yData = sample.map((v) => Number(v))

    const option = {
      tooltip: {
        trigger: 'axis',
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: xData,
        show: true,
        name: 'Sample index',
      },
      yAxis: { type: 'value', name: 'Amount' },
      series: [
        {
          type: 'line',
          data: yData,
          smooth: true,
          symbol: 'none',
          lineStyle: { color: LINE_COLOR, width: 2 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(15, 118, 110, 0.3)' },
              { offset: 1, color: 'rgba(15, 118, 110, 0.02)' },
            ]),
          },
          animation: true,
          animationDuration: 800,
          animationEasing: 'cubicOut',
        },
      ],
    }

    instanceRef.current.setOption(option)

    const onResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [data])

  useEffect(() => {
    return () => {
      instanceRef.current?.dispose()
      instanceRef.current = null
    }
  }, [])

  if (!data?.length) return <div className="loading">No data</div>

  return <div ref={chartRef} style={{ width: '100%', height }} />
}
