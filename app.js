// Router
const pages = {};
function registerPage(name, renderFn) { pages[name] = renderFn; }

const sectionMap = {
  'overview': 'overview',
  'program-performance': 'program-performance',
  'reports': 'reports',
  'report-builder': 'reports',
  'data-sources': 'data-sources',
  'data-pipeline': 'data-sources',
  'data-quality': 'data-sources',
  'ai-assistant': 'ai-assistant',
  'outcomes-impact': 'program-performance',
  'beneficiary-analytics': 'program-performance',
  'admin': 'admin'
};

function navigate(hash) {
  const page = hash.replace('#', '') || 'overview';
  const container = document.getElementById('page-container');
  if (pages[page]) {
    container.innerHTML = pages[page]();
  } else {
    container.innerHTML = pages['overview']();
  }
  // Update sidebar
  const activeSection = sectionMap[page] || page;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.remove('active-link', 'border-secondary', 'bg-secondary-container', 'text-on-secondary-container');
    link.classList.add('border-transparent', 'text-on-primary-container');
    if (link.dataset.page === (page || 'overview')) {
      link.classList.add('active-link', 'border-secondary', 'bg-secondary-container', 'text-on-secondary-container');
      link.classList.remove('border-transparent', 'text-on-primary-container');
    }
  });
  // Update top nav
  document.querySelectorAll('.top-nav-link').forEach(link => {
    link.classList.remove('active-top');
    const href = link.getAttribute('href').replace('#','');
    if (href === activeSection) {
      link.classList.add('active-top');
    }
  });
  // Scroll to top
  container.scrollTop = 0;
}

window.addEventListener('hashchange', () => navigate(location.hash));
window.addEventListener('DOMContentLoaded', () => navigate(location.hash || '#overview'));
