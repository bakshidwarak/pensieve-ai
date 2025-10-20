export interface TemplateContent {
  title: string;
  fields: TemplateField[];
}

export interface TemplateField {
  id: string;
  label: string;
  type: 'text' | 'textarea' | 'date' | 'select' | 'multiselect';
  placeholder?: string;
  options?: string[];
  required?: boolean;
}

export interface BaseButton {
  id: string;
  name: string;
  template: TemplateContent;
  icon?: string;
}

export interface ButtonTemplate extends BaseButton {
  icon: string;
  isCustom?: false;
}

export interface CustomButton extends BaseButton {
  icon?: string;
  isCustom: true;
}
