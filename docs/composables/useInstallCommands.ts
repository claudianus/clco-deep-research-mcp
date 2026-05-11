import type { InstallCommand } from '~/types';

export function useInstallCommands(): InstallCommand[] {
  return [
    {
      os: 'mac',
      label: 'macOS / Linux',
      command: 'curl -sSL https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.sh | bash',
    },
    {
      os: 'win',
      label: 'Windows',
      command: 'irm https://raw.githubusercontent.com/claudianus/maru-deep-pro-search/main/scripts/install.ps1 | iex',
    },
  ];
}
