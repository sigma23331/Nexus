// echarts 按需引入轻量入口：只注册运势趋势图实际用到的模块，
// 替代全量 import('echarts')，chunk 体积缩小约 70%。
// 若后续需要新图表类型（如柱状图），在此追加注册即可。
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

export * from 'echarts/core'
