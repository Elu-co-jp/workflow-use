import type { Node } from '@xyflow/react';

export interface StepData {
  description: string;
  output: any | null;
  timestamp: number | null;
  tabId: number | null;
  type: 'navigation' | 'click' | 'select_change' | 'input' | 'key_press' | 'scroll' | 'extract_page_content' | 'conditional_stop';
  url?: string;
  cssSelector?: string;
  xpath?: string;
  elementTag?: string;
  elementText?: string;
  selectedText?: string;
  value?: string;
  goal?: string;
  condition?: string;
  stop_message?: string;
}

export interface NodeData extends Record<string, unknown> {
  label: string;
  stepData: StepData;
}

export interface NodeConfigMenuProps {
    node: Node<NodeData> | null;
    onClose: () => void;
    workflowFilename: string | null;
}
