import React from 'react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  style,
  ...props 
}) => {
  
  const baseStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 'var(--radius-md)',
    fontWeight: 500,
    transition: 'background-color var(--transition-fast)',
    border: 'none',
    ...style
  }

  const sizes = {
    sm: { padding: 'var(--spacing-1) var(--spacing-2)', fontSize: '0.875rem' },
    md: { padding: 'var(--spacing-2) var(--spacing-4)', fontSize: '1rem' },
    lg: { padding: 'var(--spacing-3) var(--spacing-6)', fontSize: '1.125rem' }
  }

  const variants = {
    primary: { backgroundColor: 'var(--color-accent-500)', color: '#fff' },
    secondary: { backgroundColor: 'var(--color-bg-surface-hover)', color: 'var(--color-text-primary)' },
    danger: { backgroundColor: 'var(--color-danger)', color: '#fff' },
    ghost: { backgroundColor: 'transparent', color: 'var(--color-text-secondary)' }
  }

  return (
    <button 
      style={{ ...baseStyle, ...sizes[size], ...variants[variant] }} 
      {...props}
    >
      {children}
    </button>
  )
}
