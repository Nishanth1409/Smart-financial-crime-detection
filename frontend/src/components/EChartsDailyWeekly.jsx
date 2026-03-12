import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

export default function EChartsDailyWeekly({ data, unitLabel = 'Day', height = 320 }) {
  const chartRef = useRef(null)
  const instanceRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current || !data?.length) return

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current)
    }

    const displayData = data.length > 30 ? data.slice(-30) : data
    const valueKey = unitLabel === 'Week' ? 'week' : 'day'
    const labels = displayData.map((d) => `${unitLabel} ${d[valueKey]}`)
    const fraudData = displayData.map((d) => d.fraud_count)
    const notFraudData = displayData.map((d) => d.not_fraud_count)

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
      },
      legend: {
        data: ['Fraud (≥50%)', 'Not fraud (<50%)'],
        top: 0,
      },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '14%', containLabel: true },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: { rotate: displayData.length > 15 ? 35 : 0 },
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: 'Fraud (≥50%)',
          type: 'bar',
          stack: 'total',
          data: fraudData,
          itemStyle: { color: '#dc2626' },
          animationDelay: (idx) => idx * 20,
        },
        {
          name: 'Not fraud (<50%)',
          type: 'bar',
          stack: 'total',
          data: notFraudData,
          itemStyle: { color: '#0f766e' },
          animationDelay: (idx) => idx * 20,
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
  }, [data, unitLabel])

  useEffect(() => {
    return () => {
      instanceRef.current?.dispose()
      instanceRef.current = null
    }
  }, [])

  if (!data?.length) return <div className="loading">No data</div>

  return <div ref={chartRef} style={{ width: '100%', height }} />
}
