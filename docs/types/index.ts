export interface Feature {
  icon: string;
  title: string;
  description: string;
}

export interface Tool {
  name: string;
  description: string;
}

export interface PerformanceMetric {
  metric: string;
  target: string;
  implementation: string;
}

export interface BeforeAfterRow {
  before: string;
  after: string;
}

export interface InstallCommand {
  os: 'mac' | 'win';
  label: string;
  command: string;
}
