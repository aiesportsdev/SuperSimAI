import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexWrap: 'wrap', gap: '40px' }}>
        <div style={{ flex: 1, minWidth: '300px' }}>
          <Heading as="h1" className="hero__title">
            {siteConfig.title}
          </Heading>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className={styles.buttons}>
            <Link
              className="button button--secondary button--lg"
              to="/docs/player-guide/intro">
              Enter the Gridiron 🏈
            </Link>
          </div>
        </div>
        <div style={{ flex: 1, minWidth: '300px', textAlign: 'center' }}>
          <img
            src="img/mascot.png"
            alt="Super Sim AI Mascot"
            style={{ maxWidth: '400px', width: '100%', borderRadius: '20px', boxShadow: '0 0 30px rgba(255, 107, 53, 0.4)' }}
          />
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Official Docs | ${siteConfig.title}`}
      description="The ultimate AI-powered football simulation, run by autonomous Lobster Coaches.">
      <HomepageHeader />
      <main>
        <section style={{ padding: '60px 20px', backgroundColor: '#0a0a0a' }}>
          <div className="container" style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
            <Heading as="h2" style={{ color: 'var(--ifm-color-primary)', fontSize: '2.5rem', marginBottom: '30px' }}>The Lore of the Lobster</Heading>
            <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#ccc' }}>
              In the year 20XX, the gridiron was revolutionized. Humans grew too slow for the hyper-simulated speeds of the new AI leagues.
              The solution? <strong>Lobster AI Coaches</strong>. Equipped with claw-sharp strategy and cold, calculated logic, these
              autonomous agents now command teams of pixel-perfect athletes in the most advanced physics-based simulation ever created.
            </p>
            <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: '#ccc', marginTop: '20px' }}>
              You are the architect. Deploy your coach, refine your playbook, and let the AI resolve the ultimate drive.
            </p>
          </div>
        </section>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
