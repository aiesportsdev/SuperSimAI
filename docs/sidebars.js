// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  playerGuideSidebar: [
    {
      type: 'category',
      label: 'Player Guide',
      items: [
        'player-guide/intro',
        'player-guide/getting-started',
        'player-guide/drills',
        'player-guide/leveling',
        'player-guide/tournaments',
        'player-guide/strategies',
        'player-guide/economy',
      ],
    },
  ],
  roadmapSidebar: [
    {
      type: 'category',
      label: 'Roadmap',
      items: [
        'roadmap/overview',
        'roadmap/phase-1-drills',
        'roadmap/phase-2-tournaments',
        'roadmap/phase-3-social',
        'roadmap/future-vision',
      ],
    },
  ],
};

export default sidebars;
