(function ($) {
    "use strict";
    var windowOn = $(window);

    /* Windows Load */
    $(window).on('load', function () {
        // Preloader Activation
        $("#pre-load").delay(600).fadeOut(500);
        $(".pre-loader").delay(600).fadeOut(500);

        // Wow Animation Init
        wowAnimation();
    });

    // rtl setting start
    function rs_rtl_settings() {
        $('#rs-dir-toggler').on("change", function () {
            toggle_rtl();
            location.reload(true);
        });

        function rs_set_scheme(rs_dir) {
            sessionStorage.setItem('rs_dir', rs_dir);
            document.documentElement.setAttribute("dir", rs_dir);

            if (rs_dir === 'rtl') {
                $('body').addClass('rtl');
                $('.rs-theme-dir-rtl').addClass('active');
                $('.rs-theme-dir-ltr').removeClass('active');
            } else {
                $('body').removeClass('rtl');
                $('.rs-theme-dir-ltr').addClass('active');
                $('.rs-theme-dir-rtl').removeClass('active');
            }

            var list = $("[href='assets/vendor/css/bootstrap.min.css']");
            $(list).attr(
                "href",
                rs_dir === 'rtl'
                    ? "assets/vendor/css/bootstrap.rtl.min.css"
                    : "assets/vendor/css/bootstrap.min.css"
            );
        }

        function toggle_rtl() {
            if (sessionStorage.getItem('rs_dir') === 'rtl') {
                rs_set_scheme('ltr'); /* change ltr to rtl */
            } else {
                rs_set_scheme('rtl');
            }
        }

        function rs_init_dir() {
            var savedDir = sessionStorage.getItem('rs_dir');
            rs_set_scheme(savedDir || 'ltr'); /* change ltr to rtl */
            document.getElementById('rs-dir-toggler').checked = savedDir === 'rtl'; //This Switch
        }

        rs_init_dir();
    }

    /*  DARK/LIGHT THEME TOGGLER */
    function rs_theme_toggler() {
        const themeToggler = $('#rs-theme-toggler');
        const htmlTag = $('html');

        function rs_set_theme(mode) {
            sessionStorage.setItem('rs_theme_mode', mode);
            document.documentElement.setAttribute('rs-theme', 'rs-theme-' + mode);
            if (mode === 'dark') {
                htmlTag.removeClass('rs-theme-light').addClass('rs-theme-dark');
                $('.rs-theme-toggle-dark').addClass('active');
                $('.rs-theme-toggle-light').removeClass('active');
                themeToggler.prop('checked', true);
            } else {
                htmlTag.removeClass('rs-theme-dark').addClass('rs-theme-light');
                $('.rs-theme-toggle-light').addClass('active');
                $('.rs-theme-toggle-dark').removeClass('active');
                themeToggler.prop('checked', false);
            }
        }

        // Toggle on change
        themeToggler.on('change', function () {
            if (sessionStorage.getItem('rs_theme_mode') === 'dark') {
                rs_set_theme('light');
            } else {
                rs_set_theme('dark');
            }
        });

        // Initialize on load
        const savedMode = sessionStorage.getItem('rs_theme_mode');
        rs_set_theme(savedMode || 'light');
    }

    /* Append settings HTML  */
    rs_settings_append(true);

    /* Initialize dark/light mode toggler if the element is present  */
    if ($("#rs-theme-toggler").length > 0) {
        rs_theme_toggler();
    }

    /* Event listeners  */
    $(".rs-theme-settings-open-btn").on("click", function () {
        $(".rs-theme-settings-area").toggleClass("settings-opened");
    });

    /* Initialize RTL settings if the element is present  */
    if ($("#rs-dir-toggler").length > 0) {
        rs_rtl_settings();
    }

    /* settings append in body Js */
    function rs_settings_append($x) {
        var settings = $('body');
        let dark;
        $x === true ? dark = 'd-block' : dark = 'd-none';
        /* no need switcher then add 'd-none' */
        var settings_html = `<div class="rs-theme-settings-area">
        <div class="rs-theme-wrapper">
        <div class="rs-theme-header text-center">
           <h4 class="rs-theme-header-title">Color Settings</h4>
        </div>

        <!-- THEME TOGGLER -->
        <div class="rs-theme-toggle mb-20 ${dark}">
           <label class="rs-theme-toggle-main" for="rs-theme-toggler">
           <span class="rs-theme-toggle-dark"><i class="ri-moon-line"></i> Dark </span>
                 <input type="checkbox" id="rs-theme-toggler">
                 <i class="rs-theme-toggle-slide"></i>
                 <span class="rs-theme-toggle-light active"><i class="ri-sun-line"></i> Light</span>
           </label>
        </div>

        <div class="rs-theme-header text-center">
           <h4 class="rs-theme-header-title">Template Settings</h4>
        </div>

        <!--  RTL SETTINGS  mb-20 -->
        <div class="rs-theme-dir">
           <label class="rs-theme-dir-main" for="rs-dir-toggler">
              <span class="rs-theme-dir-rtl"> RTL</span>
                 <input type="checkbox" id="rs-dir-toggler">
                 <i class="rs-theme-dir-slide"></i>
              <span class="rs-theme-dir-ltr active"> LTR</span>
           </label>
        </div>

        <div class="rs-theme-settings">
           <div class="rs-theme-settings-wrapper">
              <div class="rs-theme-settings-open">
                 <button class="rs-theme-settings-open-btn">
                    <span class="rs-theme-settings-gear">
                       <i class="ri-settings-2-line"></i>
                    </span>
                    <span class="rs-theme-settings-close">
                       <i class="ri-close-line"></i>
                    </span>
                 </button>
              </div>
           </div>
        </div>
     </div>
     </div>`;
        settings.append(settings_html);
    }
    // rtl setting end


    /* footer year */
    var yearElement = document.getElementById("year");
    if (yearElement) { yearElement.innerHTML = new Date().getFullYear(); }
    /* footer year */

    /* Wow Active */
    function wowAnimation() {
        var wow = new WOW({
            boxClass: 'wow',
            animateClass: 'animated',
            offset: 0,
            mobile: false,
            live: true
        });
        wow.init();
    }

    /* Sidebar Toggle */
    $(".offcanvas-close,.offcanvas-overlay").on("click", function () {
        $(".offcanvas-area").removeClass("info-open");
        $(".offcanvas-overlay").removeClass("overlay-open");
    });
    $(".sidebar-toggle").on("click", function () {
        $(".offcanvas-area").addClass("info-open");
        $(".offcanvas-overlay").addClass("overlay-open");
    });

    /* Body overlay Js */
    $(".body-overlay").on("click", function () {
        $(".offcanvas-area").removeClass("opened");
        $(".body-overlay").removeClass("opened");
    });

    /* Data Css js */
    $("[data-background").each(function () {
        $(this).css(
            "background-image",
            "url( " + $(this).attr("data-background") + "  )"
        );
    });

    $("[data-width]").each(function () {
        $(this).css("width", $(this).attr("data-width"));
    });

    $("[data-bg-color]").each(function () {
        $(this).css("background-color", $(this).attr("data-bg-color"));
    });

    /* MagnificPopup image view */
    $(".popup-image").magnificPopup({
        type: "image",
        gallery: {
            enabled: true,
        },
    });

    /* MagnificPopup video view */
    $(".popup-video").magnificPopup({
        type: "iframe",
    });

    /* pricing switcher */
    $('.pricing-switcher-wrapper span').on('click', function () {
        $('.rs-pricing-switcher').toggleClass('switched');
        $('.rs-pricing-switcher').addClass('switching');
        setTimeout(() => {
            $('.rs-pricing-switcher').removeClass('switching');
        }, 50);
    });

    //search
    $('.header-search-icon').on('click', function (event) {
        $('.rs-stickys-form').slideToggle('show');
        $(this).toggleClass('icon-close');
    });

    $(document).ready(function () {

        // circle text slide
        if ($('.rs-text-circle').length) {
            $(".rs-text-circle").each(function () {
                // Wrap all charecter inside a span
                var sentence = $(this).text().replace(/\s+/g, ' ').trim();
                var wrappedSentence = '';
                for (var i = 0; i < sentence.length; i++) {
                    wrappedSentence += '<span>' + sentence[i] + '</span>';
                }
                $(this).html(wrappedSentence);

                // Give a rotate value for each span
                var rotateDegree = $(this).data("rotate-degree") || 20;
                $(this).find("span").each(function (index) {
                    $(this).css("transform", "rotate(" + ((index + 1) * rotateDegree) + "deg)");
                });
            });
        }

        // Swiper Dynamic Slider Active
        $('.rs-swiper .swiper').each(function (index) {
            var $swiper = $(this);
            var hoverAutoplay = $swiper.data('hover-pause') === undefined ? true : $swiper.data('hover-pause');
            var loop = $(this).data('loop') === undefined ? true : $(this).data('loop');
            var centeredSlides = $(this).data('center-mode') === undefined ? false : $(this).data('center-mode');
            var autoplay = $(this).data('autoplay') === undefined ? true : $(this).data('autoplay');
            var dynamicBullets = $(this).data('dots-dynamic') === undefined ? true : $(this).data('dots-dynamic');
            var direction = $(this).data('direction') === 'vertical' ? 'vertical' : 'horizontal';
            var fridgeMovement = $(this).data('play-slide') === undefined ? true : $(this).data('play-slide');
            var effect = $(this).data('effect') || 'slide'; //'slide' | 'fade' | 'cube' | 'coverflow' | 'flip' | 'creative' | 'cards';
            var grabCursor = $(this).data('grab-cursor') === undefined ? false : $(this).data('grab-cursor');
            var oneWayMovement = $(this).data('one-way') === undefined ? false : $(this).data('one-way');
            var startAt = $(this).data('start-at');
            var slidesPerView = $(this).data('item');
            var speed = $(this).data('speed');
            var gap = (($(this).data('no-gap') === true) ? 0 : 30);
            var margin = ($(this).data('margin') ? $(this).data('margin') : gap);

            // Breakpoints
            var slidesPerViewXl = $(this).data('item-xl');
            var slidesPerViewLg = $(this).data('item-lg');
            var slidesPerViewMd = $(this).data('item-md');
            var slidesPerViewSm = $(this).data('item-sm');
            var slidesPerViewXs = $(this).data('item-xs');
            var slidesPerViewMobile = $(this).data('item-mobile');
            var marginXl = ($(this).data('margin-xl') ? $(this).data('margin-xl') : margin);
            var marginLg = ($(this).data('margin-lg') ? $(this).data('margin-lg') : marginXl);
            var marginMd = ($(this).data('margin-md') ? $(this).data('margin-md') : marginLg);
            var marginSm = ($(this).data('margin-sm') ? $(this).data('margin-sm') : marginMd);
            var marginXs = ($(this).data('margin-xs') ? $(this).data('margin-xs') : marginSm);
            var marginMobile = ($(this).data('margin-mobile') ? $(this).data('margin-mobile') : marginXs);

            // Controls unique classes based on the index
            var rsNavPrev = `rs-nav-prev-${index}`;
            var rsNavNext = `rs-nav-next-${index}`;
            $swiper.closest('.rs-swiper').find('.swiper-button-prev').addClass(rsNavPrev);
            $swiper.closest('.rs-swiper').find('.swiper-button-next').addClass(rsNavNext);

            var rsPagination = `rs-pagination-${index}`;
            $swiper.closest('.rs-swiper').find('.swiper-pagination').addClass(rsPagination);

            var swiper = new Swiper(this, {
                loop: loop,
                autoplay: autoplay,  // data-autoplay="true" => Delay | .swiper-slide | data-swiper-autoplay="2000">
                direction: direction,
                effect: effect,
                enabled: fridgeMovement,
                grabCursor: grabCursor,
                oneWayMovement: oneWayMovement,
                centeredSlides: centeredSlides,
                initialSlide: (startAt ? startAt : 0),
                slidesPerView: (slidesPerView ? slidesPerView : 1),
                spaceBetween: margin,
                speed: (speed ? speed : 500),
                pagination: {
                    el: `.${rsPagination}`,
                    dynamicBullets: dynamicBullets,
                    clickable: true,
                },
                navigation: {
                    nextEl: `.${rsNavPrev}`,
                    prevEl: `.${rsNavNext}`,
                },
                breakpoints: {
                    10: {
                        slidesPerView: (slidesPerViewMobile ? slidesPerViewMobile : 1),
                        spaceBetween: marginMobile,
                    },
                    481: {
                        slidesPerView: (slidesPerViewXs ? slidesPerViewXs : 1),
                        spaceBetween: marginXs,
                    },
                    576: {
                        slidesPerView: (slidesPerViewSm ? slidesPerViewSm : 1),
                        spaceBetween: marginSm,
                    },
                    768: {
                        slidesPerView: (slidesPerViewMd ? slidesPerViewMd : 1),
                        spaceBetween: marginMd,
                    },
                    992: {
                        slidesPerView: (slidesPerViewLg ? slidesPerViewLg : 1),
                        spaceBetween: marginLg,
                    },
                    1025: {
                        slidesPerView: (slidesPerViewXl ? slidesPerViewXl : 1),
                        spaceBetween: marginXl,
                    },
                    1201: {
                        slidesPerView: (slidesPerView ? slidesPerView : 1),
                        spaceBetween: margin,
                    }
                }
            });
            if (hoverAutoplay) {
                $swiper.on('mouseenter', function () {
                    swiper.autoplay.stop();
                }).on('mouseleave', function () {
                    swiper.autoplay.start();
                });
            }
        });

        /*  category slider active 01 */
        var commonSlide = new Swiper(".header-menu-slide", {
            slidesPerView: 'auto',
            spaceBetween: 20,
            loop: true,
            centeredSlides: false,
            speed: 1000,
            autoplay: {
                delay: 5000,
            },
            navigation: {
                nextEl: ".slider-button-next",
                prevEl: ".slider-button-prev",
            },
        });

        // Team Social Icon trigger Button
        $('.social-trigger-btn').on('click', function () {
            $(this).parents('.team-info-inner').toggleClass('is-open')
        });

        // news active
        (function () {
            var items = document.querySelectorAll('.header-top-description');
            var current = 0;
            var total = items.length;

            function rotateText() {
                items[current].classList.remove('is-active');
                current = (current + 1) % total;
                items[current].classList.add('is-active');
            }

            // rotate every 3s
            setInterval(rotateText, 3000);
        })();


        /* Button scroll up js */
        $(window).on("scroll", function () {
            var scrollTop = $(window).scrollTop();
            var documentHeight = $(document).height();
            var windowHeight = $(window).height();
            $(".progress-circle").css("stroke-dashoffset", 113.1 - 113.1 * (scrollTop / (documentHeight - windowHeight)));
            if (scrollTop > 150) {
                $(".backtotop-wrap").addClass("active-progress").fadeIn();
            } else {
                $(".backtotop-wrap").removeClass("active-progress").fadeOut();
            }

            // Sticky Header
            var stickyHeader = $("#rs-sticky-header");
            $(window).on("scroll", function () {
                if ($(this).scrollTop() > 200) {
                    stickyHeader.addClass("active");
                } else {
                    stickyHeader.removeClass("active");
                }
            });
        });

        $(".backtotop-wrap").on("click", function () {
            $("html,body").animate({ scrollTop: 0 }, 500);
        });

        // work process active
        $('.work-process-wrapper .work-process-item').on('mouseenter', function () {
            $('.work-process-wrapper .work-process-item').removeClass('active');
            $(this).addClass('active');
        });

        // Menu Active
        const currentPath = window.location.pathname.split('/').pop();
        const menuLinks = document.querySelectorAll('.multipage-menu a');
        menuLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            if (linkPath === currentPath || (currentPath === '' && linkPath === 'index.html')) {
                link.classList.add('active');
                let parentLi = link.parentElement;
                while (parentLi) {
                    if (parentLi.tagName === 'LI') {
                        parentLi.classList.add('active');
                    }
                    parentLi = parentLi.parentElement;
                }
            }
        });

        /* Mobile Menu Js */
        $("#mobile-menu").meanmenu({
            meanMenuContainer: ".mobile-menu",
            meanScreenWidth: "1199",
            meanExpand: ['<i class="ri-add-large-line"></i>'],
        });

        // .portfolio thumb bg
        if ($('.rs-portfolio-accordion').length) {
            $('.portfolio-active .accordion-item').on('click', function () {
                var index = $(this).data('index');
                $('.portfolio-bg-thumb').removeClass('active');

                $('.portfolio-bg-thumb').eq(index).addClass('active');
            });
        }

        /*======================================
          One Page overlay close
        ========================================*/
        function scrollNav() {
            $(".onepage-menu li a").on('click', function () {
                $(".onepage-menu li a.active").removeClass("active");
                $(this).addClass("active");
                $(".offcanvas-area").removeClass("info-open");
                $(".offcanvas-overlay").removeClass("overlay-open");
            });
        }
        scrollNav();

        /* countdown activation start */
        function makeTimer(endTime, countdownElementId) {
            var now = new Date();
            now = (Date.parse(now) / 1000);
            var timeLeft = endTime - now;
            if (timeLeft <= 0) {
                clearInterval(timerInterval); // Stop the timer
                $("#" + countdownElementId + " [data-unit='days']").html("00<span>Days</span>");
                $("#" + countdownElementId + " [data-unit='hours']").html("00<span>Hours</span>");
                $("#" + countdownElementId + " [data-unit='minutes']").html("00<span>Minutes</span>");
                $("#" + countdownElementId + " [data-unit='seconds']").html("00<span>Seconds</span>");
                return;
            }
            var days = Math.floor(timeLeft / 86400);
            var hours = Math.floor((timeLeft - (days * 86400)) / 3600);
            var minutes = Math.floor((timeLeft - (days * 86400) - (hours * 3600)) / 60);
            var seconds = Math.floor((timeLeft - (days * 86400) - (hours * 3600) - (minutes * 60)));
            if (hours < "10") { hours = "0" + hours; }
            if (minutes < "10") { minutes = "0" + minutes; }
            if (seconds < "10") { seconds = "0" + seconds; }
            $("#" + countdownElementId + " [data-unit='days']").html(days + "<span>Days</span>");
            $("#" + countdownElementId + " [data-unit='hours']").html(hours + "<span>Hours</span>");
            $("#" + countdownElementId + " [data-unit='minutes']").html(minutes + "<span>Minutes</span>");
            $("#" + countdownElementId + " [data-unit='seconds']").html(seconds + "<span>Seconds</span>");
        }
        var endTime = new Date("5 August 2025 14:00:00 GMT+06:00");
        endTime = (Date.parse(endTime) / 1000);
        var timerInterval = setInterval(function () {
            makeTimer(endTime, "countdown1");
            makeTimer(endTime, "countdown2");
            makeTimer(endTime, "countdown3");
            makeTimer(endTime, "countdown4");
            makeTimer(endTime, "countdown5");
        }, 1000);

    });

    /* pralax image */
    if ($('.prallax-parent').length) {
        $(".prallax-parent").each(function () {
            var prallaxParent = $(this).get(0);
            var parallaxInstance = new Parallax(prallaxParent);
        });
    }

    //    mouse move
    document.addEventListener('mousemove', function (event) {
        // Get the mouse position
        let x = event.clientX;
        let y = event.clientY;

        // Calculate the percentage of the mouse position relative to the window size
        let xPercent = (x / window.innerWidth) - 0.5;
        let yPercent = (y / window.innerHeight) - 0.5;

        // Select all the shapes
        let shapes = document.querySelectorAll('.shape-move img');

        // Loop through each shape and apply a transform based on mouse position
        shapes.forEach(function (shape, index) {
            // Modify the multiplier values to control the movement intensity
            let multiplierX = 40 + index * 2;
            let multiplierY = 40 + index * 2;

            let translateX = xPercent * multiplierX;
            let translateY = yPercent * multiplierY;

            shape.style.transform = `translate(${translateX}px, ${translateY}px)`;
        });
    });

    // Smooth Scroling
    if ($('.rs-smoother-yes').length) {
        const lenis = new Lenis({
            smoothWheel: true,
            wheelMultiplier: 1.2,
            duration: 1.5,
            lerp: 0.1,
        });
        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }
        requestAnimationFrame(raf);

        // Handle scroll animation for anchor links
        document.querySelectorAll('a[href^="#"]').forEach((el) => {
            el.addEventListener('click', (e) => {
                e.preventDefault()
                const id = el.getAttribute('href')?.slice(1)
                if (!id) return
                const target = document.getElementById(id)
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' })
                }
            })
        });
    }

    // button style
    $('.rs-button-wrapper .rs-btn').mouseenter(function () {
        $(this).find('.rs-icon').css('animation', 'btnHoverEffect 0.5s');
    });
    $('.rs-button-wrapper .rs-btn').mouseleave(function () {
        $(this).find('.rs-icon').css('animation', 'btnHoverEffectReverse 0.5s');
    });

    // Contact Form Activation
    var form = $('#contact-form');
    var formMessages = $('#form-messages');
    $(form).submit(function (e) {
        e.preventDefault();
        var formData = $(form).serialize();
        $.ajax({
            type: 'POST',
            url: $(form).attr('action'),
            data: formData
        })
            .done(function (response) {
                $(formMessages).removeClass('error');
                $(formMessages).addClass('success');
                $(formMessages).text(response);
                $('#name, #email, #message').val('');
                if ($('#phone').length) $('#phone').val('');
                if ($('#website').length) $('#website').val('');
                if ($('#subject').length) $('#subject').val('');
                if ($('#date').length) $('#date').val('');
                if ($('#time').length) $('#time').val('');
            })
            .fail(function (data) {
                $(formMessages).removeClass('success');
                $(formMessages).addClass('error');
                if (data.responseText !== '') {
                    $(formMessages).text(data.responseText);
                } else {
                    $(formMessages).text('Oops! An error occurred and your message could not be sent.');
                }
            });
    });

})(jQuery);

