import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

const BAR_COLOR = '#0f766e'
const BAR_COLOR_HOVER = '#0d9488'

export default function EChartsBar({ data, valueKey = 'count', labelKey = 'label', height = 280 }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current || !data?.length) return

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current)
    }

    const labels = data.map((d) => String(d[labelKey]))
    const values = data.map((d) => Number(d[valueKey]))

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { rotate: labels.length > 6 ? 25 : 0 },
      },
      yAxis: { type: 'value' },
      series: [
        {
          type: 'bar',
          data: values,
          itemStyle: {
            color: BAR_COLOR,
          },
          emphasis: {
            itemStyle: { color: BAR_COLOR_HOVER },
          },
          animationDelay: (idx) => idx * 50,
        },
      ],
      animation: true,
      animationDuration: 600,
      animationEasing: 'cubicOut',
    }

    instanceRef.current.setOption(option)

    const onResize = () => instanceRef.current?.resize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [data, valueKey, labelKey])

  useEffect(() => {
    return () => {
      instanceRef.current?.dispose()
      instanceRef.current = null
    }
  }, [])

  if (!data?.length) return <div className="loading">No data</div>

  return <div ref={chartRef} style={{ width: '100%', height }} />
}
