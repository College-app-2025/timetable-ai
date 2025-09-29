import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import { ChartData, TimeSeriesData } from '../types';
import { CHART_COLORS } from '../utils/constants';

interface BarChartProps {
  data: ChartData[];
  title: string;
  xAxisKey: string;
  yAxisKey: string;
  color?: string;
  height?: number;
}

export const AnalyticsBarChart: React.FC<BarChartProps> = ({
  data,
  title,
  xAxisKey,
  yAxisKey,
  color = CHART_COLORS[0],
  height = 300
}) => {
  return (
    <div className="card">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xAxisKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Bar 
                dataKey={yAxisKey} 
                fill={color}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

interface PieChartProps {
  data: ChartData[];
  title: string;
  height?: number;
}

export const AnalyticsPieChart: React.FC<PieChartProps> = ({
  data,
  title,
  height = 300
}) => {
  return (
    <div className="card">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

interface LineChartProps {
  data: TimeSeriesData[];
  title: string;
  xAxisKey: string;
  yAxisKey: string;
  color?: string;
  height?: number;
}

export const AnalyticsLineChart: React.FC<LineChartProps> = ({
  data,
  title,
  xAxisKey,
  yAxisKey,
  color = CHART_COLORS[0],
  height = 300
}) => {
  return (
    <div className="card">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xAxisKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey={yAxisKey} 
                stroke={color}
                strokeWidth={2}
                dot={{ fill: color, strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

interface AreaChartProps {
  data: TimeSeriesData[];
  title: string;
  xAxisKey: string;
  yAxisKey: string;
  color?: string;
  height?: number;
}

export const AnalyticsAreaChart: React.FC<AreaChartProps> = ({
  data,
  title,
  xAxisKey,
  yAxisKey,
  color = CHART_COLORS[0],
  height = 300
}) => {
  return (
    <div className="card">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div style={{ height }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xAxisKey} 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                stroke="#666"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Area 
                type="monotone" 
                dataKey={yAxisKey} 
                stroke={color}
                fill={color}
                fillOpacity={0.3}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

interface HeatmapProps {
  data: { day: string; time: string; value: number }[];
  title: string;
  height?: number;
}

export const AnalyticsHeatmap: React.FC<HeatmapProps> = ({
  data,
  title,
  height = 300
}) => {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const timeSlots = ['9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];

  const getIntensity = (value: number) => {
    if (value === 0) return 'bg-gray-100';
    if (value <= 25) return 'bg-blue-200';
    if (value <= 50) return 'bg-blue-400';
    if (value <= 75) return 'bg-blue-600';
    return 'bg-blue-800';
  };

  const getValue = (day: string, time: string) => {
    const item = data.find(d => d.day === day && d.time === time);
    return item ? item.value : 0;
  };

  return (
    <div className="card">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div style={{ height }}>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="text-left text-sm font-medium text-gray-700 p-2">Day</th>
                  {timeSlots.map(time => (
                    <th key={time} className="text-center text-xs font-medium text-gray-700 p-2">
                      {time}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {days.map(day => (
                  <tr key={day}>
                    <td className="text-sm font-medium text-gray-700 p-2">{day}</td>
                    {timeSlots.map(time => (
                      <td key={time} className="text-center p-2">
                        <div
                          className={`w-8 h-8 rounded ${getIntensity(getValue(day, time))} flex items-center justify-center text-xs text-white font-medium`}
                          title={`${day} ${time}: ${getValue(day, time)}% utilization`}
                        >
                          {getValue(day, time) > 0 && getValue(day, time)}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Low utilization</span>
          <div className="flex space-x-1">
            <div className="w-4 h-4 bg-gray-100 rounded"></div>
            <div className="w-4 h-4 bg-blue-200 rounded"></div>
            <div className="w-4 h-4 bg-blue-400 rounded"></div>
            <div className="w-4 h-4 bg-blue-600 rounded"></div>
            <div className="w-4 h-4 bg-blue-800 rounded"></div>
          </div>
          <span>High utilization</span>
        </div>
      </div>
    </div>
  );
};

// Export all chart components
export {
  AnalyticsBarChart,
  AnalyticsPieChart,
  AnalyticsLineChart,
  AnalyticsAreaChart,
  AnalyticsHeatmap
};
