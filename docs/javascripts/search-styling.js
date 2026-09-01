/*
 * Stop-gap styling for the search overlay.
 *
 * Zensical builds the search dialog at runtime and mounts it in an open shadow
 * root attached to a bare <div> at the end of <body>, so neither zensical.toml
 * nor docs/stylesheets/extra.css can reach it. See the TODO under
 * [project.plugins.search] in zensical.toml: this file should be removed once
 * zensical ships hooks for styling the search interface.
 *
 * The class names inside the shadow root are minified and are regenerated on
 * every zensical release, so nothing here refers to them. Instead we walk the
 * tree down from the search <input> and tag the structural elements with our
 * own data-cscs-search attributes, and the injected stylesheet targets those.
 * If the structure ever changes the walk bails out and the stock styling is
 * left untouched.
 *
 * Colours are read from the --color-* custom properties that zensical defines
 * in the light DOM. Those inherit through the shadow boundary, so the palette
 * is tuned in docs/stylesheets/extra.css and stays scheme-aware for free.
 */
(function () {
  "use strict";

  var STYLES = [
    /* base font size, for anything that does not set its own */
    '[data-cscs-search="root"] { --font-size: 19px; }',

    /* backdrop: a real dim, so the page clearly reads as "behind" */
    '[data-cscs-search="backdrop"] {',
    '  background-color: rgb(var(--color-backdrop) / 0.55);',
    '}',

    /* panel: opaque, bordered and lifted off the page */
    '[data-cscs-search="panel"] {',
    '  background-color: rgb(var(--color-background));',
    '  border: 1px solid rgb(var(--color-foreground) / 0.18);',
    '  box-shadow: 0 1.5rem 4rem rgb(0 0 0 / 0.35);',
    '}',

    /* input: a recessed field with an accent focus ring */
    '[data-cscs-search="input"] {',
    '  padding: 6px 10px;',
    '  border-radius: var(--border-radius-2);',
    '  background-color: rgb(var(--color-background-subtle));',
    '  box-shadow: inset 0 0 0 1px rgb(var(--color-foreground) / 0.12);',
    '  transition: box-shadow 0.15s ease;',
    '}',
    '[data-cscs-search="input"]:focus-within {',
    '  box-shadow: inset 0 0 0 2px var(--md-accent-fg-color, #526cfe);',
    '}',
    '[data-cscs-search="input"] input {',
    '  font-size: 19px;',
    '  letter-spacing: normal;',
    '}',

    /* the controls row already separates itself with the field background */
    '[data-cscs-search="controls"] { border-bottom: none; }',
    '[data-cscs-search="results"] {',
    '  border-top: 1px solid rgb(var(--color-foreground) / 0.12);',
    '  color: rgb(var(--color-foreground) / 0.86);',
    '}',

    /* results typography */
    '[data-cscs-search="results"] h3 { font-size: 15px; }',
    '[data-cscs-search="results"] h2 { font-size: 18px; }',
    '[data-cscs-search="results"] h2 code { font-size: 17px; }',
    '[data-cscs-search="results"] menu li {',
    '  font-size: 15px;',
    '  color: rgb(var(--color-foreground) / 0.62);',
    '}',
    '[data-cscs-search="results"] h2 + div { font-size: 16px; }',
    '[data-cscs-search="results"] h2 + div code { font-size: 15px; }',
    /* code spans get their own tint rather than --color-background-subtle,
       which also drives the input field and the hover band and so has to sit
       much lighter than the panel in dark mode */
    '[data-cscs-search="results"] code {',
    '  background-color: rgb(var(--color-foreground) / 0.06);',
    '}',

    /* filters sidebar: part of the panel, so opaque like the panel */
    '[data-cscs-search="sidebar"] {',
    '  background-color: rgb(var(--color-background-subtle));',
    '}',
    '[data-cscs-search="sidebar"] h3 { font-size: 19px; }',
    '[data-cscs-search="sidebar"] h4 { font-size: 17px; }',
    '[data-cscs-search="sidebar"] li { font-size: 15px; }'
  ].join("\n");

  /* Tag the structural elements of the dialog. Returns false and changes
     nothing if the tree does not have the shape we expect. */
  function tag(shadowRoot) {
    var input = shadowRoot.querySelector('input[role="combobox"]') ||
                shadowRoot.querySelector("input");
    if (!input) {
      return false;
    }

    var field    = input.parentElement;
    var controls = field && field.parentElement;
    var content  = controls && controls.parentElement;
    var panel    = content && content.parentElement;
    var root     = panel && panel.parentElement;
    if (!root || root.parentNode !== shadowRoot) {
      return false;
    }

    var backdrop = root.firstElementChild;
    var results  = controls.nextElementSibling;
    var sidebar  = content.nextElementSibling;
    if (backdrop === panel) {
      backdrop = null;
    }

    var parts = {
      root: root,
      backdrop: backdrop,
      panel: panel,
      content: content,
      controls: controls,
      input: field,
      results: results,
      sidebar: sidebar
    };
    Object.keys(parts).forEach(function (name) {
      if (parts[name]) {
        parts[name].setAttribute("data-cscs-search", name);
      }
    });
    return true;
  }

  function adopt(shadowRoot) {
    try {
      var sheet = new CSSStyleSheet();
      sheet.replaceSync(STYLES);
      shadowRoot.adoptedStyleSheets = shadowRoot.adoptedStyleSheets.concat(sheet);
      return;
    } catch (error) {
      /* fall through to a plain <style> element */
    }
    var style = document.createElement("style");
    style.textContent = STYLES;
    shadowRoot.appendChild(style);
  }

  function decorate(host) {
    var shadowRoot = host.shadowRoot;
    adopt(shadowRoot);
    tag(shadowRoot);

    /* The host is attached as soon as the search component mounts, but its
       contents are only rendered once the search index arrives from the
       worker, so the first tag() above usually finds nothing. The dialog is
       also re-rendered on every keystroke. Re-tag on mutation, both to catch
       that first render and so a future rewrite cannot silently drop the
       tags. Only childList is observed, so our own setAttribute calls cannot
       feed back into this. */
    var pending = false;
    new MutationObserver(function () {
      if (pending) {
        return;
      }
      pending = true;
      requestAnimationFrame(function () {
        pending = false;
        tag(shadowRoot);
      });
    }).observe(shadowRoot, { childList: true, subtree: true });
  }

  /* The overlay host is the only direct child of <body> with a shadow root:
     the bundle's other attachShadow call is mermaid, which uses mode "closed"
     on an element that is never a direct child of <body>. */
  function findHost() {
    var children = document.body.children;
    for (var i = 0; i < children.length; i++) {
      if (children[i].shadowRoot) {
        return children[i];
      }
    }
    return null;
  }

  var done = false;
  function attempt() {
    if (done) {
      return true;
    }
    var host = findHost();
    if (!host) {
      return false;
    }
    done = true;
    decorate(host);
    return true;
  }

  if (!attempt()) {
    /* The host is created when the search component mounts, which happens
       asynchronously after the bundle loads. With navigation.instant the
       bundle is not re-run on navigation, so this only needs to fire once. */
    var observer = new MutationObserver(function () {
      if (attempt()) {
        observer.disconnect();
      }
    });
    observer.observe(document.body, { childList: true });
  }
})();
