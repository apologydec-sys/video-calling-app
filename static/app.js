document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('.hero-media');
  const hoverItems = document.querySelectorAll('.person-badge, .signature');

  if (scene) {
    const setParallax = (event) => {
      const x = (event.clientX / window.innerWidth - 0.5) * 18;
      const y = (event.clientY / window.innerHeight - 0.5) * 18;

      scene.style.transform = `perspective(1600px) rotateX(${(-y).toFixed(2)}deg) rotateY(${x.toFixed(2)}deg)`;

      hoverItems.forEach((item, index) => {
        const offsetX = (index % 2 === 0 ? 1 : -1) * x * (index + 1) * 0.45;
        const offsetY = y * (index + 1) * 0.45;
        item.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
      });
    };

    document.addEventListener('pointermove', setParallax);

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (reduceMotion.matches) {
      document.removeEventListener('pointermove', setParallax);
      scene.style.transform = 'none';
      hoverItems.forEach((item) => {
        item.style.transform = 'none';
      });
    }
  }

  const revealItems = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  }, { threshold: 0.16 });

  revealItems.forEach((item) => observer.observe(item));
});
