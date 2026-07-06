import React from 'react';
import styles from './Shell.module.css';

interface ShellProps {
  header: React.ReactNode;
  sidebar: React.ReactNode;
  workspace: React.ReactNode;
  inspector?: React.ReactNode;
  activity?: React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({
  header,
  sidebar,
  workspace,
  inspector,
  activity,
}) => {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>{header}</header>
      <div className={styles.body}>
        <aside className={styles.sidebar}>{sidebar}</aside>
        <main className={styles.workspace}>{workspace}</main>
        {inspector && <aside className={styles.inspector}>{inspector}</aside>}
        {activity && <aside className={styles.activity}>{activity}</aside>}
      </div>
    </div>
  );
};
