import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

const CustomCursor = () => {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [isHovering, setIsHovering] = useState(false);
    const canvasRef = useRef(null);
    const particles = useRef([]);

    useEffect(() => {
        const mouseMove = (e) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
            // Add particles on move
            for (let i = 0; i < 3; i++) {
                particles.current.push({
                    x: e.clientX,
                    y: e.clientY,
                    size: Math.random() * 4 + 1,
                    speedX: Math.random() * 2 - 1,
                    speedY: Math.random() * 2 - 1,
                    life: 1,
                    color: `hsl(${Math.random() * 60 + 160}, 100%, 70%)` // Teal to Blue range
                });
            }
        };

        const handleMouseOver = (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('.clickable') || e.target.closest('.tab')) {
                setIsHovering(true);
            } else {
                setIsHovering(false);
            }
        };

        window.addEventListener("mousemove", mouseMove);
        window.addEventListener("mouseover", handleMouseOver);

        // Canvas Animation Loop
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        const resizeCanvas = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const animateParticles = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.current.forEach((p, index) => {
                p.life -= 0.02;
                p.x += p.speedX;
                p.y += p.speedY;
                p.size *= 0.95;

                if (p.life <= 0) {
                    particles.current.splice(index, 1);
                } else {
                    ctx.fillStyle = p.color;
                    ctx.globalAlpha = p.life;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                }
            });

            requestAnimationFrame(animateParticles);
        };
        animateParticles();

        return () => {
            window.removeEventListener("mousemove", mouseMove);
            window.removeEventListener("mouseover", handleMouseOver);
            window.removeEventListener('resize', resizeCanvas);
        };
    }, []);

    return (
        <>
            <canvas
                ref={canvasRef}
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    pointerEvents: 'none',
                    zIndex: 9998
                }}
            />
            <motion.div
                className="cursor-dot"
                animate={{
                    x: mousePosition.x - 6,
                    y: mousePosition.y - 6,
                    scale: isHovering ? 2.5 : 1
                }}
                transition={{
                    type: "spring",
                    stiffness: 500,
                    damping: 28
                }}
                style={{
                    position: "fixed",
                    top: 0,
                    left: 0,
                    width: 12,
                    height: 12,
                    backgroundColor: "#e29578", // Coral dot
                    borderRadius: "50%",
                    pointerEvents: "none",
                    zIndex: 10000,
                    boxShadow: "0 0 15px rgba(226, 149, 120, 0.6)",
                    mixBlendMode: "screen"
                }}
            />
        </>
    );
};

export default CustomCursor;
