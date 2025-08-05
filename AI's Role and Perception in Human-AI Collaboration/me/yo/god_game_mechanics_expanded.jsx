import React from "react";

export default function GodGameMechanicsExpanded() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-800 to-orange-600 text-white p-8 font-sans">
      <section className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4">Designing Your Own God</h1>
        <p className="text-xl max-w-2xl mx-auto mb-4">
          Ever dreamed of being a god? This project delves into the intricate mechanics of designing your own god game—where power, control, and creativity collide to shape virtual worlds.
        </p>
        <p className="text-lg max-w-2xl mx-auto">
          Tired of the same old gameplay? Here you’ll learn how to create a god game that's deeply engaging, blending strategic mechanics with narrative depth. Explore how player decisions impact simulated societies and forge emergent stories.
        </p>
      </section>

      <section className="mb-20">
        <h2 className="text-4xl font-bold mb-6 text-center">The God Game Concept</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white/10 p-6 rounded-2xl shadow-xl">
            <h3 className="text-2xl font-semibold mb-2">What Makes a God Game?</h3>
            <p>God games put players in omnipotent roles—granting them power to create, destroy, and guide civilizations. These games blend simulation, strategy, and sandbox elements to offer players god-like control over systems.</p>
          </div>
          <div className="bg-white/10 p-6 rounded-2xl shadow-xl">
            <h3 className="text-2xl font-semibold mb-2">Iconic Titles</h3>
            <p>Explore masterpieces like <em>SimCity</em>, <em>Black & White</em>, and <em>Spore</em>—each offering unique systems, aesthetics, and philosophies on player control and world-building.</p>
          </div>
          <div className="bg-white/10 p-6 rounded-2xl shadow-xl">
            <h3 className="text-2xl font-semibold mb-2">Why We Love Them</h3>
            <p>There’s a deep psychological appeal to god games—giving players the freedom to explore power, make ethical choices, and experiment with world-building without real-world consequences.</p>
          </div>
        </div>
      </section>

      <section className="mb-20">
        <h2 className="text-4xl font-bold mb-6 text-center">Crafting Core Mechanics</h2>
        <div className="space-y-6 max-w-4xl mx-auto">
          <p><strong>World Simulation:</strong> Design dynamic environments where weather, ecosystems, and resource flows interact. These systems must react to player input and evolve over time to stay engaging.</p>
          <p><strong>Player Agency:</strong> Define how players manipulate the world—from terraforming to nudging population behavior. The freedom and consequences of these interactions are central to the god game experience.</p>
          <p><strong>Deity Abilities:</strong> Develop god powers—miracles, punishments, environmental control—that offer satisfying feedback while introducing strategic depth.</p>
        </div>
      </section>

      <section className="mb-20">
        <h2 className="text-4xl font-bold mb-6 text-center">Designing Meaningful Interactions</h2>
        <div className="space-y-6 max-w-4xl mx-auto">
          <p><strong>Building Relationships:</strong> Let players interact with in-game entities—nurturing faith, sowing fear, or guiding communities. These connections personalize the experience and foster emotional investment.</p>
          <p><strong>Moral Systems:</strong> Introduce moral choices—should players smite or forgive? These dilemmas shape not only outcomes but also how players perceive their godhood.</p>
          <p><strong>Emergence & Chaos:</strong> Balance control with unpredictability. Let systems evolve in unexpected ways, giving players surprise challenges and storytelling opportunities.</p>
        </div>
      </section>

      <section className="mb-20">
        <h2 className="text-4xl font-bold mb-6 text-center">Storytelling Through Systems</h2>
        <div className="space-y-6 max-w-4xl mx-auto">
          <p><strong>Gameplay as Narrative:</strong> Use your mechanics to tell stories. Civilizations may rebel, natural disasters can be omens, and every decision writes part of the world’s lore.</p>
          <p><strong>Player-Driven Stories:</strong> Encourage emergent storytelling. The best god games feel personal because they let players define their own narratives through action.</p>
          <p><strong>Replayability:</strong> Dynamic systems and branching paths make each playthrough different. Emergent behavior creates a living world that never behaves the same way twice.</p>
        </div>
      </section>

      <section className="mb-20">
        <h2 className="text-4xl font-bold mb-6 text-center">Game Design Advice</h2>
        <div className="space-y-6 max-w-4xl mx-auto">
          <p><strong>Start Small:</strong> Begin with a core loop—like growing a village—and build outward. Focus on depth before expanding scope.</p>
          <p><strong>Work Within Limits:</strong> Constraints foster creativity. Define clear rules for how your world works and use those to design interactions.</p>
          <p><strong>Iterate and Test:</strong> Let players experiment. Gather feedback early and often, using it to shape better mechanics and smoother systems.</p>
        </div>
      </section>

      <section className="text-center">
        <h2 className="text-4xl font-bold mb-4">Start Designing</h2>
        <p className="mb-6 max-w-xl mx-auto">
          Ready to shape destiny? Use the tools below to begin crafting your divine playground.
        </p>
        <button className="bg-pink-600 hover:bg-pink-700 transition px-6 py-3 text-lg rounded-xl shadow-lg">
          Launch Creator Tool
        </button>
      </section>
    </main>
  );
}
