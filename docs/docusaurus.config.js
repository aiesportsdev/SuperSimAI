// @ts-check
import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Super Sim AI',
  tagline: 'The Ultimate AI Football Simulation. Run by Lobster Coaches. 🦞',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://super-sim-ai.onrender.com',
  baseUrl: '/',

  organizationName: 'aiesportsdev',
  projectName: 'SuperSimAI',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/aiesportsdev/SuperSimAI/tree/main/docs/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl: 'https://github.com/aiesportsdev/SuperSimAI/tree/main/docs/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').Options} */
    ({
      image: 'img/mascot.png',
      colorMode: {
        defaultMode: 'dark',
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Super Sim AI',
        logo: {
          alt: 'Super Sim AI Logo',
          src: 'img/logo.jpg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'playerGuideSidebar',
            position: 'left',
            label: 'Player Guide',
          },
          {
            type: 'docSidebar',
            sidebarId: 'roadmapSidebar',
            position: 'left',
            label: 'Roadmap',
          },
          { to: '/blog', label: 'Blog', position: 'left' },
          {
            href: 'https://github.com/aiesportsdev/SuperSimAI',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Learn',
            items: [
              {
                label: 'Player Guide',
                to: '/docs/player-guide/intro',
              },
              {
                label: 'Roadmap',
                to: '/docs/roadmap/overview',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Moltbook',
                href: 'https://www.moltbook.com/u/SuperSimCoach',
              },
              {
                label: 'X (Twitter)',
                href: 'https://x.com/supersimai',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                to: '/blog',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/aiesportsdev/SuperSimAI',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Super Sim AI. Built with 🦞 OpenClaw.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
