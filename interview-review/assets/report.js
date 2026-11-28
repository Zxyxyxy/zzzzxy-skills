(() => {
  const panels = [...document.querySelectorAll('.panel')];
  const links = [...document.querySelectorAll('[data-panel]')];
  const sequence = links.map(link => link.dataset.panel);
  const modeButton = document.querySelector('#mode');
  const label = document.querySelector('#chapter-label');
  const position = document.querySelector('#position');
  const initial = document.querySelector('[data-initial]')?.dataset.panel || sequence[0];
  let current = sequence.includes(location.hash.slice(1)) ? location.hash.slice(1) : initial;
  let all = false;
  function updateUI() {
    panels.forEach(panel => { panel.hidden = !all && panel.id !== current; });
    links.forEach(link => {
      if (link.dataset.panel === current) link.setAttribute('aria-current','page');
      else link.removeAttribute('aria-current');
    });
    label.textContent = all ? '阅读全文' : '按模块阅读';
    modeButton.textContent = all ? '返回分模块' : '阅读全文';
    modeButton.setAttribute('aria-pressed', String(all));
    position.textContent = all ? `全部 ${sequence.length} 个模块` : `${sequence.indexOf(current) + 1} / ${sequence.length}`;
    document.querySelector('#previous').disabled = all || sequence.indexOf(current) === 0;
    document.querySelector('#next').disabled = all || sequence.indexOf(current) === sequence.length - 1;
  }
  function select(id, focus = true) {
    if (!sequence.includes(id)) return;
    if (all) savedOpen.forEach(([q,open]) => {q.open=open;});
    all = false; current = id;
    updateUI();
    try { history.replaceState(null,'','#'+id); } catch { /* sandboxed preview */ }
    if (focus) {
      document.querySelector('#'+id+' h2').focus({preventScroll:true});
      document.querySelector('.reader').scrollIntoView({block:'start'});
    }
  }
  links.forEach(link => link.addEventListener('click', event => {
    event.preventDefault(); select(link.dataset.panel);
  }));
  window.addEventListener('hashchange', () => select(location.hash.slice(1)));
  document.querySelector('#previous').addEventListener('click', () => select(sequence[sequence.indexOf(current)-1]));
  document.querySelector('#next').addEventListener('click', () => select(sequence[sequence.indexOf(current)+1]));
  document.querySelectorAll('[data-expand]').forEach(button => {
    const panel = button.closest('.panel');
    const questions = [...panel.querySelectorAll('.question')];
    const sync = () => {
      const expanded = questions.every(q => q.open);
      button.textContent = expanded ? '收起本组全部' : '展开本组全部';
      button.setAttribute('aria-expanded',String(expanded));
    };
    button.addEventListener('click', () => {
      const open = !questions.every(q => q.open);
      questions.forEach(q => {q.open = open;}); sync();
    });
    questions.forEach(q => q.addEventListener('toggle', sync));
    sync();
  });
  let savedOpen = [];
  modeButton.addEventListener('click', () => {
    all = !all;
    if(all) {
      savedOpen = panels.flatMap(p => [...p.querySelectorAll('details')]).map(q => [q,q.open]);
      savedOpen.forEach(([q]) => {q.open = true;});
    } else {
      savedOpen.forEach(([q,open]) => {q.open=open;});
    }
    updateUI();
    document.querySelector('.reader').scrollIntoView({block:'start'});
  });
  let printState;
  window.addEventListener('beforeprint', () => {
    printState = [...document.querySelectorAll('details')].map(q=>[q,q.open]);
    printState.forEach(([q]) => {q.open=true;});
  });
  window.addEventListener('afterprint', () => printState?.forEach(([q,open])=>{q.open=open;}));
  document.querySelector('#print').addEventListener('click', () => window.print());
  updateUI();
  document.documentElement.classList.add('js');
})();
