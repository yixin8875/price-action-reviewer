export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface Instrument {
  id: number;
  symbol: string;
  name: string;
  exchange: string;
  instrument_type: 'stock' | 'futures' | 'forex' | 'crypto';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface KLine {
  id: number;
  instrument: number;
  trade_date: string;
  trade_time?: string;
  open_price: string;
  high_price: string;
  low_price: string;
  close_price: string;
  volume: string;
  amount?: string;
  period: '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M';
}

export interface Indicator {
  id: number;
  name: string;
  indicator_type: 'trend' | 'momentum' | 'volatility' | 'volume' | 'custom';
  parameters: Record<string, any>;
  description?: string;
  is_active: boolean;
}

export interface Pattern {
  id: number;
  name: string;
  pattern_type: 'candlestick' | 'chart' | 'harmonic' | 'custom';
  description?: string;
  reliability_score?: number;
}

export interface ReviewRecord {
  id: number;
  instrument: number;
  instrument_name?: string;
  title: string;
  review_date: string;
  timeframe: string;
  entry_price?: string;
  exit_price?: string;
  stop_loss?: string;
  take_profit?: string;
  position_type?: 'long' | 'short';
  analysis_notes?: string;
  outcome?: 'win' | 'loss' | 'breakeven' | 'pending';
  rating?: number;
  tags?: string[];
  patterns?: number[];
  indicators?: number[];
  created_at: string;
  updated_at: string;
}

export interface TradeLog {
  id: number;
  review: number;
  entry_time: string;
  exit_time?: string;
  entry_price: string;
  exit_price?: string;
  quantity: string;
  position_type: 'long' | 'short';
  profit_loss?: string;
  profit_loss_percentage?: string;
  notes?: string;
}

export interface DashboardStats {
  total_instruments: number;
  total_reviews: number;
  total_trades: number;
  win_rate?: number;
  total_profit_loss?: string;
}
