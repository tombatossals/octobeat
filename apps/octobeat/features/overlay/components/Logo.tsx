"use client";

export function Logo() {
    return (
        <div className="pointer-events-none fixed left-4 top-4 z-50 flex items-center rounded-xl border border-white/10 bg-gray-800/60 pl-2 pr-4 shadow-2xl backdrop-blur-md">
            <img
                src="/logo.png"
                alt="Octobeat logo"
                className="h-15 w-auto object-contain"
            />

            <span
                className="mx-1.5 h-8 w-px bg-white"
                style={{
                    boxShadow:
                        "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151",
                }}
                aria-hidden="true"
            />

            <span
                className="text-4xl font-black leading-none tracking-[-0.08em] text-white"
                style={{
                    textShadow:
                        "1px 1px 0 #374151, -1px -1px 0 #374151, 1px -1px 0 #374151, -1px 1px 0 #374151, 1px 0 0 #374151, -1px 0 0 #374151, 0 1px 0 #374151, 0 -1px 0 #374151",
                }}
            >
                Octobeat
            </span>
        </div>
    );
}
