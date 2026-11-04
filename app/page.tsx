import markup from "../generated/pageMarkup.json";

/**
 * Intentional server render of the prevalidated story HTML.
 * HTML is generated locally from version-controlled script JSON, using
 * HTML escaping for all text fields (scripts/build_site.py).
 * Browser behaviour is progressively enhanced by public/assets/site.js.
 * The static HTML remains readable without JavaScript.
 */
export default function HomePage() {
  return <div id="story-experience" dangerouslySetInnerHTML={{ __html: markup.html }} />;
}
