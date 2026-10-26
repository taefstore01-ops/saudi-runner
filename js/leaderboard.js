/* Global leaderboard (Firebase Firestore + anonymous auth).
   Exposes window.SR_BOARD; the game works without it (offline / no config). */
(() => {
  'use strict';
  const SDK = 'https://www.gstatic.com/firebasejs/10.12.2/';
  const config = window.SAUDIRUN_FIREBASE;

  // ISO week in UTC, e.g. "2026-W44"; the weekly board resets when it changes
  function weekKey(d = new Date()) {
    const t = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
    const day = t.getUTCDay() || 7;
    t.setUTCDate(t.getUTCDate() + 4 - day);
    const y = t.getUTCFullYear();
    const w = Math.ceil(((t - Date.UTC(y, 0, 1)) / 864e5 + 1) / 7);
    return `${y}-W${String(w).padStart(2, '0')}`;
  }

  // names: 2-14 letters/digits/spaces, no rude words (kids play this game)
  const BAD = ['كلب', 'حمار', 'غبي', 'حيوان', 'زق', 'خرا', 'تفو', 'سكس', 'شرموط', 'قحب', 'منيك', 'نيك', 'زب', 'طيز', 'لعن',
    'fuck', 'shit', 'bitch', 'sex', 'porn', 'dick', 'ass', 'nigg', 'fag', 'cunt', 'whore', 'slut', 'kill'];
  function checkName(raw) {
    const name = String(raw || '').replace(/\s+/g, ' ').trim();
    if (name.length < 2) return { error: 'الاسم قصير، اكتب حرفين على الأقل' };
    if (name.length > 14) return { error: 'الاسم طويل، الحد 14 حرفاً' };
    if (!/^[\p{L}\p{N} _-]+$/u.test(name)) return { error: 'استخدم حروفاً وأرقاماً فقط' };
    const flat = name.toLowerCase().replace(/[\s_-]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه');
    if (BAD.some(w => flat.includes(w))) return { error: 'اختر اسماً لطيفاً من فضلك' };
    return { name };
  }

  let fb = null;          // { db, uid, fs }
  let readyPromise = null;
  function ready() {
    if (!config) return Promise.reject(new Error('no-config'));
    if (readyPromise) return readyPromise;
    readyPromise = (async () => {
      const [app, auth, fs] = await Promise.all([
        import(SDK + 'firebase-app.js'), import(SDK + 'firebase-auth.js'), import(SDK + 'firebase-firestore.js')]);
      const a = app.initializeApp(config);
      const au = auth.getAuth(a);
      const cred = au.currentUser ? { user: au.currentUser } : await auth.signInAnonymously(au);
      fb = { db: fs.getFirestore(a), uid: cred.user.uid, fs };
      return fb;
    })();
    readyPromise.catch(() => { readyPromise = null; });   // allow a retry later (e.g. back online)
    return readyPromise;
  }

  /** Saves the player's score: raises best / this week's best, never lowers them. */
  async function submit({ name, score, hero, region }) {
    const { db, uid, fs } = await ready();
    const ref = fs.doc(db, 'scores', uid);
    const snap = await fs.getDoc(ref);
    const old = snap.exists() ? snap.data() : null;
    const week = weekKey();
    const best = Math.max(score, old ? old.best : 0);
    const weekBest = Math.max(score, old && old.week === week ? old.weekBest : 0);
    if (old && old.name === name && old.best === best && old.week === week && old.weekBest === weekBest) return old;
    const entry = { name, best, weekBest, week, hero, region, updated: fs.serverTimestamp() };
    await fs.setDoc(ref, entry);
    return entry;
  }

  /** Top players: kind 'week' or 'all'. */
  async function top(kind, n = 50) {
    const { db, uid, fs } = await ready();
    const col = fs.collection(db, 'scores');
    const q = kind === 'week'
      ? fs.query(col, fs.where('week', '==', weekKey()), fs.orderBy('weekBest', 'desc'), fs.limit(n))
      : fs.query(col, fs.orderBy('best', 'desc'), fs.limit(n));
    const snap = await fs.getDocs(q);
    return snap.docs.map(d => {
      const v = d.data();
      return { me: d.id === uid, name: v.name, score: kind === 'week' ? v.weekBest : v.best, hero: v.hero, region: v.region };
    });
  }

  /** The player's own row and rank (1-based), or null if they have no score yet. */
  async function mine(kind) {
    const { db, uid, fs } = await ready();
    const snap = await fs.getDoc(fs.doc(db, 'scores', uid));
    if (!snap.exists()) return null;
    const v = snap.data();
    const week = weekKey();
    if (kind === 'week' && v.week !== week) return null;
    const score = kind === 'week' ? v.weekBest : v.best;
    const col = fs.collection(db, 'scores');
    const q = kind === 'week'
      ? fs.query(col, fs.where('week', '==', week), fs.where('weekBest', '>', score))
      : fs.query(col, fs.where('best', '>', score));
    const above = (await fs.getCountFromServer(q)).data().count;
    return { rank: above + 1, name: v.name, score, hero: v.hero, region: v.region, me: true };
  }

  window.SR_BOARD = { enabled: !!config, ready, submit, top, mine, checkName, weekKey };
})();
