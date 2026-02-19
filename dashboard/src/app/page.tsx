'use client'

import Link from 'next/link'
import { useState, useEffect, useRef } from 'react'
import {
    Phone,
    Brain,
    Bell,
    BookOpen,
    LayoutDashboard,
    Mail,
    Heart,
    Shield,
    ArrowRight,
    ChevronDown,
    Activity,
    Sparkles,
    Clock,
    Users,
    Star,
} from 'lucide-react'

/* ──────────────────────────────────────────────
   Animated counter hook
   ────────────────────────────────────────────── */
function useCounter(end: number, duration = 2000) {
    const [count, setCount] = useState(0)
    const ref = useRef<HTMLDivElement>(null)
    const started = useRef(false)

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && !started.current) {
                    started.current = true
                    const start = performance.now()
                    const step = (now: number) => {
                        const progress = Math.min((now - start) / duration, 1)
                        setCount(Math.floor(progress * end))
                        if (progress < 1) requestAnimationFrame(step)
                    }
                    requestAnimationFrame(step)
                }
            },
            { threshold: 0.3 }
        )
        if (ref.current) observer.observe(ref.current)
        return () => observer.disconnect()
    }, [end, duration])

    return { count, ref }
}

function StatCounterItem({
    end,
    suffix,
    label,
    icon: Icon,
}: {
    end: number
    suffix: string
    label: string
    icon: React.ComponentType<{ className?: string }>
}) {
    const { count, ref } = useCounter(end)
    return (
        <div ref={ref} className="flex items-center gap-3 text-white">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/15">
                <Icon className="h-5 w-5" />
            </div>
            <div>
                <p className="text-2xl font-bold">
                    {count}
                    {suffix}
                </p>
                <p className="text-xs text-blue-200">{label}</p>
            </div>
        </div>
    )
}

/* ──────────────────────────────────────────────
   Fade-in-on-scroll wrapper
   ────────────────────────────────────────────── */
function FadeIn({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
    const ref = useRef<HTMLDivElement>(null)
    const [visible, setVisible] = useState(false)

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting) setVisible(true)
            },
            { threshold: 0.15 }
        )
        if (ref.current) observer.observe(ref.current)
        return () => observer.disconnect()
    }, [])

    return (
        <div
            ref={ref}
            className={`transition-all duration-700 ${visible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'} ${className}`}
            style={{ transitionDelay: `${delay}ms` }}
        >
            {children}
        </div>
    )
}

/* ══════════════════════════════════════════════
   LANDING PAGE
   ══════════════════════════════════════════════ */
export default function LandingPage() {
    const [scrolled, setScrolled] = useState(false)

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 40)
        window.addEventListener('scroll', onScroll, { passive: true })
        return () => window.removeEventListener('scroll', onScroll)
    }, [])

    return (
        <div className="min-h-screen bg-white text-gray-900">
            {/* ── Sticky Nav ─────────────────────────── */}
            <header
                className={`fixed top-0 z-50 w-full transition-all duration-300 ${scrolled
                        ? 'bg-white/80 shadow-sm backdrop-blur-xl'
                        : 'bg-transparent'
                    }`}
            >
                <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
                    <Link href="/" className="flex items-center gap-2 text-xl font-bold tracking-tight">
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25">
                            <Heart className="h-5 w-5" />
                        </div>
                        <span className={scrolled ? 'text-gray-900' : 'text-white'}>ClaraCare</span>
                    </Link>

                    <nav className="hidden items-center gap-8 md:flex">
                        {['Features', 'How It Works', 'For Families'].map((item) => (
                            <a
                                key={item}
                                href={`#${item.toLowerCase().replace(/\s+/g, '-')}`}
                                className={`text-sm font-medium transition-colors hover:text-blue-600 ${scrolled ? 'text-gray-600' : 'text-white/80 hover:text-white'
                                    }`}
                            >
                                {item}
                            </a>
                        ))}
                    </nav>

                    <Link
                        href="/dashboard"
                        className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-gray-900 shadow-lg shadow-black/5 transition-all hover:shadow-xl hover:shadow-black/10 active:scale-95"
                    >
                        Open Dashboard
                    </Link>
                </div>
            </header>

            {/* ── Hero ────────────────────────────────── */}
            <section className="relative overflow-hidden bg-gradient-to-br from-blue-700 via-indigo-700 to-violet-800 pb-24 pt-32 md:pb-36 md:pt-44">
                {/* Decorative blobs */}
                <div className="pointer-events-none absolute -left-40 -top-40 h-[500px] w-[500px] rounded-full bg-blue-500/20 blur-3xl" />
                <div className="pointer-events-none absolute -bottom-20 right-0 h-[400px] w-[400px] rounded-full bg-violet-500/20 blur-3xl" />
                <div className="pointer-events-none absolute left-1/2 top-1/3 h-[300px] w-[300px] -translate-x-1/2 rounded-full bg-indigo-400/10 blur-3xl" />

                <div className="relative mx-auto max-w-5xl px-6 text-center">
                    <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-medium text-white/90 backdrop-blur-sm">
                        <Sparkles className="h-4 w-4 text-amber-300" />
                        AI-Powered Elder Care Companion
                    </div>

                    <h1 className="mx-auto max-w-4xl text-4xl font-extrabold leading-tight tracking-tight text-white md:text-6xl md:leading-[1.1]">
                        Daily check-ins that keep
                        <br />
                        <span className="bg-gradient-to-r from-sky-300 to-cyan-200 bg-clip-text text-transparent">
                            families connected
                        </span>
                    </h1>

                    <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-blue-100/80 md:text-xl">
                        Clara calls your loved ones every day, has warm conversations,
                        monitors cognitive health with clinical-grade NLP, and sends you
                        a real-time wellness dashboard — so you&apos;re never out of the loop.
                    </p>

                    <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
                        <Link
                            href="/dashboard"
                            className="group flex items-center gap-2 rounded-full bg-white px-8 py-4 text-base font-bold text-gray-900 shadow-2xl shadow-black/20 transition-all hover:-translate-y-0.5 hover:shadow-3xl active:scale-95"
                        >
                            Try the Dashboard
                            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                        <a
                            href="#how-it-works"
                            className="flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-8 py-4 text-base font-semibold text-white backdrop-blur-sm transition-all hover:bg-white/20"
                        >
                            See How It Works
                            <ChevronDown className="h-4 w-4" />
                        </a>
                    </div>
                </div>

                {/* Floating dashboard preview */}
                <div className="mx-auto mt-16 max-w-4xl px-6">
                    <div className="overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-1 shadow-2xl shadow-black/30 backdrop-blur-xl">
                        <div className="rounded-xl bg-gradient-to-b from-gray-50 to-white p-6 md:p-8">
                            {/* Mock dashboard header */}
                            <div className="mb-6 flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500">Good morning</p>
                                    <p className="text-xl font-bold text-gray-900">Dorothy&apos;s Dashboard</p>
                                </div>
                                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-emerald-500 text-sm font-bold text-white shadow-lg shadow-green-500/30">
                                    75
                                </div>
                            </div>
                            {/* Mock stats row */}
                            <div className="grid grid-cols-3 gap-3">
                                {[
                                    { label: 'Cognitive Score', value: '75/100', color: 'from-blue-500 to-indigo-500' },
                                    { label: 'Conversations', value: '12', color: 'from-violet-500 to-purple-500' },
                                    { label: 'Active Alerts', value: '2', color: 'from-amber-500 to-orange-500' },
                                ].map((stat) => (
                                    <div key={stat.label} className="rounded-xl bg-gray-50 p-4">
                                        <p className="text-xs font-medium text-gray-500">{stat.label}</p>
                                        <p className={`mt-1 bg-gradient-to-r ${stat.color} bg-clip-text text-2xl font-bold text-transparent`}>
                                            {stat.value}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── Stats Bar ───────────────────────────── */}
            <section className="-mt-1 bg-gradient-to-r from-blue-600 to-indigo-600 py-8">
                <div className="mx-auto grid max-w-5xl grid-cols-2 gap-6 px-6 md:grid-cols-4">
                    {(
                        [
                            { end: 5, suffix: '', label: 'Cognitive Metrics Tracked', icon: Brain },
                            { end: 24, suffix: '/7', label: 'Always Available', icon: Clock },
                            { end: 100, suffix: '%', label: 'NLP Accuracy', icon: Activity },
                            { end: 30, suffix: 's', label: 'Alert Response Time', icon: Bell },
                        ] as const
                    ).map((stat, i) => (
                        <StatCounterItem
                            key={i}
                            end={stat.end}
                            suffix={stat.suffix}
                            label={stat.label}
                            icon={stat.icon}
                        />
                    ))}
                </div>
            </section>

            {/* ── Features ────────────────────────────── */}
            <section id="features" className="bg-white py-24">
                <div className="mx-auto max-w-6xl px-6">
                    <FadeIn className="text-center">
                        <p className="text-sm font-semibold uppercase tracking-wider text-blue-600">Features</p>
                        <h2 className="mx-auto mt-3 max-w-xl text-3xl font-extrabold tracking-tight md:text-4xl">
                            Everything your family needs in one place
                        </h2>
                    </FadeIn>

                    <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {[
                            {
                                icon: Phone,
                                title: 'AI Voice Calls',
                                desc: 'Clara calls daily with warm, personalized conversations — adapting tone and topics to each patient.',
                                gradient: 'from-blue-500 to-indigo-500',
                                shadow: 'shadow-blue-500/20',
                            },
                            {
                                icon: Brain,
                                title: 'Cognitive Tracking',
                                desc: '5 NLP metrics — vocabulary diversity, topic coherence, repetition, word-finding pauses, response latency.',
                                gradient: 'from-violet-500 to-purple-500',
                                shadow: 'shadow-violet-500/20',
                            },
                            {
                                icon: Bell,
                                title: 'Smart Alerts',
                                desc: 'Instant alerts to family when cognitive scores deviate from baseline — low, medium, or high severity.',
                                gradient: 'from-amber-500 to-orange-500',
                                shadow: 'shadow-amber-500/20',
                            },
                            {
                                icon: BookOpen,
                                title: 'Nostalgia Therapy',
                                desc: 'Clara weaves era-specific memories into conversations — music, events, culture — to boost engagement.',
                                gradient: 'from-pink-500 to-rose-500',
                                shadow: 'shadow-pink-500/20',
                            },
                            {
                                icon: LayoutDashboard,
                                title: 'Family Dashboard',
                                desc: 'Real-time wellness view: cognitive trends, conversation history, mood tracking, and downloadable reports.',
                                gradient: 'from-emerald-500 to-teal-500',
                                shadow: 'shadow-emerald-500/20',
                            },
                            {
                                icon: Mail,
                                title: 'Daily Digests',
                                desc: 'Automated email summaries with highlights, recommendations, and cognitive scores delivered every morning.',
                                gradient: 'from-sky-500 to-cyan-500',
                                shadow: 'shadow-sky-500/20',
                            },
                        ].map((feature, i) => (
                            <FadeIn key={feature.title} delay={i * 100}>
                                <div className="group relative rounded-2xl border border-gray-100 bg-white p-6 transition-all hover:-translate-y-1 hover:shadow-xl">
                                    <div
                                        className={`mb-4 inline-flex items-center justify-center rounded-xl bg-gradient-to-br ${feature.gradient} p-3 shadow-lg ${feature.shadow}`}
                                    >
                                        <feature.icon className="h-6 w-6 text-white" />
                                    </div>
                                    <h3 className="text-lg font-bold">{feature.title}</h3>
                                    <p className="mt-2 text-sm leading-relaxed text-gray-600">{feature.desc}</p>
                                </div>
                            </FadeIn>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── How It Works ────────────────────────── */}
            <section id="how-it-works" className="bg-gray-50 py-24">
                <div className="mx-auto max-w-5xl px-6">
                    <FadeIn className="text-center">
                        <p className="text-sm font-semibold uppercase tracking-wider text-blue-600">How It Works</p>
                        <h2 className="mt-3 text-3xl font-extrabold tracking-tight md:text-4xl">
                            Three simple steps to peace of mind
                        </h2>
                    </FadeIn>

                    <div className="mt-16 grid gap-8 md:grid-cols-3">
                        {[
                            {
                                step: '01',
                                title: 'Clara Calls',
                                desc: 'Schedule daily check-ins. Clara calls your loved one with warm, engaging conversations tailored to their personality and preferences.',
                                icon: Phone,
                                gradient: 'from-blue-600 to-indigo-600',
                            },
                            {
                                step: '02',
                                title: 'AI Analyzes',
                                desc: 'Our NLP engine extracts 5 cognitive metrics from every conversation, comparing against a personalized baseline built over time.',
                                icon: Brain,
                                gradient: 'from-violet-600 to-purple-600',
                            },
                            {
                                step: '03',
                                title: 'Family Stays Informed',
                                desc: 'View real-time cognitive trends, receive instant alerts for deviations, and get daily digest emails — all from one dashboard.',
                                icon: Users,
                                gradient: 'from-emerald-600 to-teal-600',
                            },
                        ].map((item, i) => (
                            <FadeIn key={item.step} delay={i * 150}>
                                <div className="relative flex flex-col items-center text-center">
                                    {/* Step number */}
                                    <span className="mb-4 text-5xl font-black text-gray-200">{item.step}</span>
                                    <div
                                        className={`mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br ${item.gradient} shadow-xl`}
                                    >
                                        <item.icon className="h-7 w-7 text-white" />
                                    </div>
                                    <h3 className="text-xl font-bold">{item.title}</h3>
                                    <p className="mt-3 text-sm leading-relaxed text-gray-600">{item.desc}</p>
                                </div>
                            </FadeIn>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── For Families ───────────────────────── */}
            <section id="for-families" className="bg-white py-24">
                <div className="mx-auto max-w-6xl px-6">
                    <div className="grid items-center gap-12 md:grid-cols-2">
                        <FadeIn>
                            <p className="text-sm font-semibold uppercase tracking-wider text-blue-600">For Families</p>
                            <h2 className="mt-3 text-3xl font-extrabold tracking-tight md:text-4xl">
                                Peace of mind,
                                <br />
                                even from miles away
                            </h2>
                            <p className="mt-5 text-base leading-relaxed text-gray-600">
                                Distance shouldn&apos;t mean disconnection. ClaraCare bridges the gap between
                                busy lives and aging loved ones — providing daily companionship, clinical-grade
                                cognitive monitoring, and immediate family alerts when something changes.
                            </p>

                            <div className="mt-8 space-y-4">
                                {[
                                    { icon: Shield, text: 'HIPAA-aware data handling and secure storage' },
                                    { icon: Heart, text: 'Warm, empathetic conversations — not robotic scripts' },
                                    { icon: Star, text: 'Personalized to their life story, hobbies, and era' },
                                    { icon: Activity, text: 'Clinical-grade NLP tracking 5 cognitive dimensions' },
                                ].map(({ icon: Icon, text }) => (
                                    <div key={text} className="flex items-start gap-3">
                                        <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100">
                                            <Icon className="h-3.5 w-3.5 text-blue-600" />
                                        </div>
                                        <p className="text-sm text-gray-700">{text}</p>
                                    </div>
                                ))}
                            </div>
                        </FadeIn>

                        <FadeIn delay={200}>
                            {/* Glassmorphism card cluster */}
                            <div className="relative">
                                {/* Background decorative card */}
                                <div className="absolute -bottom-4 -right-4 h-full w-full rounded-3xl bg-gradient-to-br from-blue-100 to-indigo-100" />
                                <div className="relative space-y-4 rounded-3xl border border-gray-200 bg-white p-6 shadow-xl">
                                    {/* Mini alert card */}
                                    <div className="flex items-start gap-3 rounded-xl bg-amber-50 p-4">
                                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-100">
                                            <Bell className="h-4 w-4 text-amber-600" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold text-amber-900">Cognitive Alert</p>
                                            <p className="mt-0.5 text-xs text-amber-700">Vocabulary diversity dropped 15% below baseline</p>
                                        </div>
                                    </div>
                                    {/* Mini conversation card */}
                                    <div className="rounded-xl border border-gray-100 bg-gray-50 p-4">
                                        <div className="flex items-center gap-2">
                                            <div className="h-2 w-2 rounded-full bg-green-500" />
                                            <p className="text-xs font-medium text-gray-500">Today&apos;s Call — 8 min</p>
                                        </div>
                                        <p className="mt-2 text-sm text-gray-700">
                                            &ldquo;Dorothy talked about her grandchildren visiting last weekend.
                                            Mood: happy. Engagement: high.&rdquo;
                                        </p>
                                    </div>
                                    {/* Mini score card */}
                                    <div className="flex items-center justify-between rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 p-4 text-white">
                                        <div>
                                            <p className="text-xs font-medium text-blue-200">Cognitive Score</p>
                                            <p className="text-2xl font-bold">75 / 100</p>
                                        </div>
                                        <div className="text-sm font-semibold text-emerald-300">↑ Stable</div>
                                    </div>
                                </div>
                            </div>
                        </FadeIn>
                    </div>
                </div>
            </section>

            {/* ── CTA ─────────────────────────────────── */}
            <section className="relative overflow-hidden bg-gradient-to-br from-blue-700 via-indigo-700 to-violet-800 py-24">
                <div className="pointer-events-none absolute -left-20 -top-20 h-[300px] w-[300px] rounded-full bg-blue-500/20 blur-3xl" />
                <div className="pointer-events-none absolute -bottom-10 right-0 h-[250px] w-[250px] rounded-full bg-violet-500/20 blur-3xl" />

                <FadeIn className="relative mx-auto max-w-3xl px-6 text-center">
                    <h2 className="text-3xl font-extrabold text-white md:text-4xl">
                        Start caring smarter today
                    </h2>
                    <p className="mx-auto mt-4 max-w-lg text-lg text-blue-100/80">
                        Give your loved ones the daily companionship they deserve — and give
                        yourself the peace of mind you need.
                    </p>
                    <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
                        <Link
                            href="/dashboard"
                            className="group flex items-center gap-2 rounded-full bg-white px-8 py-4 text-base font-bold text-gray-900 shadow-2xl shadow-black/20 transition-all hover:-translate-y-0.5 hover:shadow-3xl active:scale-95"
                        >
                            Open Dashboard
                            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                        </Link>
                    </div>
                </FadeIn>
            </section>

            {/* ── Footer ──────────────────────────────── */}
            <footer className="border-t border-gray-200 bg-white py-12">
                <div className="mx-auto max-w-6xl px-6">
                    <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
                        <div className="flex items-center gap-2 text-lg font-bold tracking-tight">
                            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white">
                                <Heart className="h-4 w-4" />
                            </div>
                            ClaraCare
                        </div>
                        <p className="text-sm text-gray-500">
                            AI Elder Care Companion — Built with ❤️ for families everywhere.
                        </p>
                        <div className="flex gap-6 text-sm text-gray-500">
                            <Link href="/dashboard" className="transition-colors hover:text-gray-900">Dashboard</Link>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}
