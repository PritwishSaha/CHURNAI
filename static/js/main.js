/* ChurnAI front-end behaviour.
   Everything here is progressive enhancement: pages work without it. */

(() => {
    'use strict';

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const $ = (selector, root = document) => root.querySelector(selector);
    const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
    const nextFrame = (fn) => requestAnimationFrame(() => requestAnimationFrame(fn));

    const easeOut = (t) => 1 - Math.pow(1 - t, 3);

    function tween(from, to, duration, onUpdate) {
        if (reduceMotion || duration <= 0) {
            onUpdate(to);
            return;
        }
        const start = performance.now();
        const step = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            onUpdate(from + (to - from) * easeOut(progress));
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }

    /* ---------- Header ---------- */

    const header = $('#site-header');
    if (header) {
        const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    /* ---------- Mobile navigation ---------- */

    const toggle = $('.nav-toggle');
    const nav = $('#site-nav');

    if (toggle && nav) {
        const setOpen = (open) => {
            toggle.setAttribute('aria-expanded', String(open));
            toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
            nav.classList.toggle('is-open', open);
        };

        toggle.addEventListener('click', () => {
            setOpen(toggle.getAttribute('aria-expanded') !== 'true');
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && nav.classList.contains('is-open')) {
                setOpen(false);
                toggle.focus();
            }
        });

        nav.addEventListener('click', (event) => {
            if (event.target.closest('a')) setOpen(false);
        });

        window.matchMedia('(min-width: 821px)').addEventListener('change', (event) => {
            if (event.matches) setOpen(false);
        });
    }

    /* ---------- Risk dial ---------- */

    const ZONE_LABEL = { low: 'Low risk', medium: 'Medium risk', high: 'High risk' };

    function zoneFor(gauge, value) {
        if (value < parseFloat(gauge.dataset.low)) return 'low';
        if (value < parseFloat(gauge.dataset.thr)) return 'medium';
        return 'high';
    }

    function setGauge(gauge, rawValue) {
        const value = Math.min(Math.max(rawValue, 0), 100);
        const fill = $('.gauge-fill', gauge);
        const needle = $('.gauge-needle', gauge);
        const number = $('[data-gauge-num]', gauge);
        const state = $('[data-gauge-state]', gauge);
        const zone = zoneFor(gauge, value);

        gauge.classList.remove('is-low', 'is-medium', 'is-high');
        gauge.classList.add(`is-${zone}`);

        if (fill) fill.style.strokeDasharray = `${value} 100`;
        if (needle) needle.style.transform = `rotate(${180 + value * 1.8}deg)`;
        if (state) state.textContent = ZONE_LABEL[zone];

        if (number) {
            const from = typeof gauge._shown === 'number' ? gauge._shown : 0;
            tween(from, value, 1100, (current) => {
                number.textContent = current.toFixed(1);
            });
            gauge._shown = value;
        }

        gauge.setAttribute(
            'aria-label',
            `Churn probability ${value.toFixed(1)} percent, ${ZONE_LABEL[zone].toLowerCase()} zone`
        );
    }

    $$('[data-gauge]').forEach((gauge) => {
        const target = parseFloat(gauge.dataset.value);
        if (Number.isNaN(target)) return;

        const number = $('[data-gauge-num]', gauge);
        if (number && !reduceMotion) number.textContent = '0.0';
        gauge._shown = 0;

        nextFrame(() => {
            gauge.classList.add('is-ready');
            setGauge(gauge, target);
        });

        const cycle = (gauge.dataset.cycle || '')
            .split(',')
            .map(parseFloat)
            .filter((n) => !Number.isNaN(n));

        if (cycle.length > 1 && !reduceMotion) {
            let index = 0;
            window.setInterval(() => {
                if (document.hidden) return;
                index = (index + 1) % cycle.length;
                setGauge(gauge, cycle[index]);
            }, 3800);
        }
    });

    /* ---------- Count-up figures and animated bars ---------- */

    $$('[data-count]').forEach((element) => {
        const target = parseFloat(element.dataset.count);
        if (Number.isNaN(target) || reduceMotion) return;

        const decimals = parseInt(element.dataset.decimals || '0', 10);
        const suffix = element.dataset.suffix || '';

        element.textContent = `${(0).toFixed(decimals)}${suffix}`;
        tween(0, target, 1100, (current) => {
            element.textContent = `${current.toFixed(decimals)}${suffix}`;
        });
    });

    $$('[data-bars]').forEach((element) => {
        nextFrame(() => element.classList.add('is-ready'));
    });

    /* ---------- Local times (stored in UTC) ---------- */

    $$('time[data-local]').forEach((element) => {
        const date = new Date(element.getAttribute('datetime'));
        if (Number.isNaN(date.getTime())) return;
        const options = element.hasAttribute('data-short')
            ? { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
            : { dateStyle: 'medium', timeStyle: 'short' };
        element.textContent = date.toLocaleString(undefined, options);
    });

    /* ---------- Predict form ---------- */

    const form = $('#predict-form');

    if (form) {
        const money = (value) =>
            `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

        const formatters = {
            tenure: (v) => `${v} ${v === '1' ? 'year' : 'years'}`,
            balance: money,
            salary: money,
            has_card: (v) => (v === '1' ? 'Yes' : 'No'),
            active_member: (v) => (v === '1' ? 'Yes' : 'No'),
        };

        const previews = $$('[data-preview]', form);
        const meter = $('[data-meter]', form);
        const filledLabel = $('[data-filled]', form);

        const readValue = (name) => {
            const control = form.elements[name];
            return control ? String(control.value || '').trim() : '';
        };

        const updateSummary = () => {
            let filled = 0;

            previews.forEach((node) => {
                const name = node.dataset.preview;
                const value = readValue(name);

                if (value) {
                    filled += 1;
                    node.textContent = formatters[name] ? formatters[name](value) : value;
                    node.classList.remove('is-empty');
                } else {
                    node.textContent = 'Not set';
                    node.classList.add('is-empty');
                }
            });

            if (meter) meter.style.width = `${(filled / previews.length) * 100}%`;
            if (filledLabel) filledLabel.textContent = `${filled} of ${previews.length} details added`;
        };

        form.addEventListener('input', updateSummary);
        form.addEventListener('change', updateSummary);
        window.addEventListener('pageshow', updateSummary);
        updateSummary();

        // Scrolling over a focused number box should scroll the page, not change the value.
        form.addEventListener('wheel', () => {
            const active = document.activeElement;
            if (active && active.type === 'number') active.blur();
        }, { passive: true });

        const submit = $('button[type="submit"]', form);
        const submitLabel = submit ? $('[data-label]', submit) : null;
        const idleText = submitLabel ? submitLabel.textContent : '';

        const resetSubmit = () => {
            if (!submit) return;
            submit.disabled = false;
            submit.classList.remove('is-loading');
            if (submitLabel) submitLabel.textContent = idleText;
        };

        form.addEventListener('submit', () => {
            if (!submit) return;
            submit.classList.add('is-loading');
            if (submitLabel) submitLabel.textContent = 'Scoring';
            // Disable after the browser has collected the form data.
            window.setTimeout(() => { submit.disabled = true; }, 0);
        });

        // Coming back with the browser's back button must not leave the button stuck.
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) resetSubmit();
        });
    }
})();
