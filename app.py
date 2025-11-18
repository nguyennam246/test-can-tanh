import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime
from pathlib import Path


st.set_page_config(
    page_title="6 Hạt Giống Tâm",
    page_icon="🌿",
    layout="centered",
)

# CSS tối ưu mobile - hỗ trợ dark/light mode
st.markdown(
    """
    <style>
    /* Giới hạn chiều rộng nội dung, căn giữa */
    .main .block-container {
        max-width: 720px;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        margin: 0 auto;
    }

    /* Tiêu đề chính */
    h1, h2, h3 {
        font-weight: 600;
    }

    /* Đoạn mô tả & text chính, giữ màu theo theme, chỉ chỉnh spacing */
    p {
        line-height: 1.6;
    }

    /* Nút: full width trên mobile, vừa phải trên desktop */
    .stButton > button {
        border-radius: 999px;
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
    }

    /* Radio: khoảng cách vừa phải, dễ bấm bằng ngón tay */
    .stRadio > label {
        font-weight: 500;
    }
    .stRadio > div {
        padding-top: 0.15rem;
        padding-bottom: 0.15rem;
    }

    /* Ẩn khung lớn quanh icon phân tích – chỉ giữ icon */
    .trait-icon-wrapper {
        padding: 0;
        margin: 0.4rem 0 0.6rem 0;
        background: transparent !important;
        border-radius: 0;
    }

    /* Icon căn tánh: to, nhưng thoáng */
    .trait-icon {
        font-size: 2.4rem;
        text-align: center;
    }

    /* Khối kết quả - hỗ trợ dark/light mode */
    .result-card {
        border-radius: 12px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.75rem;
        background-color: rgba(255, 255, 255, 0.03);
    }

    /* MOBILE FIRST */
    @media (max-width: 600px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 1.5rem;
        }
        h2, h3 {
            font-size: 1.2rem;
        }

        p {
            font-size: 0.95rem;
        }

        .stButton > button {
            width: 100% !important;
        }

        .result-card {
            padding: 0.8rem 0.9rem;
        }
    }

    /* LIGHT & DARK: không set background, chỉ dùng màu tương đối */
    /* Câu nhắc "Hãy trả lời bằng phản ứng thật..." đã set color riêng rồi, giữ nguyên. */
    </style>
    """,
    unsafe_allow_html=True
)

# CSV_FILE đã bỏ - app không lưu kết quả

TEMPERAMENTS = {
    "duc": {"label": "Dục", "desc": "Khuynh hướng tìm cảm giác dễ chịu, thoả mãn."},
    "san": {"label": "Sân", "desc": "Khuynh hướng phản ứng bằng bực tức, chống đối."},
    "si": {"label": "Si", "desc": "Khuynh hướng mơ hồ, lúng túng, thiếu rõ ràng."},
    "tin": {"label": "Tín", "desc": "Khuynh hướng dựa vào niềm tin, giá trị, đạo lý sống."},
    "niem": {"label": "Niệm", "desc": "Khả năng nhận biết trực tiếp thân–tâm, có mặt với trải nghiệm."},
    "tue": {"label": "Tuệ", "desc": "Khả năng thấy rõ nhân–quả, bản chất vấn đề và logic vận hành."},
}

# Bảng ánh xạ hardcoded cho đất hợp, cách chăm, đạo hành, lời khuyên
MAPPING = {
    "Dục": {
        "dat_hop": "KỶ LUẬT – ÍT KÍCH THÍCH – LÀNH MẠNH",
        "cach_cham": "Kỷ luật nhỏ → làm đều; hạn chế kích thích mạnh.",
        "dao_hanh": "Hữu Nguyện Hành",
        "dao_hanh_giai_thich": "Làm đều đặn, có kế hoạch, có kỷ luật.",
        "loi_khuyen": "Chọn vài nguyên tắc nhỏ nhưng rõ, làm đều mỗi ngày để năng lượng ham muốn chạy đúng đường.",
        "cau_dat": "KỶ LUẬT GIẢI QUYẾT TẤT CẢ",
        "canh_bao_lech": "Dục mạnh nhưng Niệm/Tuệ yếu → dễ chạy theo cảm xúc nhất thời.",
        "dinh_huong_1d4": "Ít kích thích → làm đều.",
        "icon": "🔥",
        "color": "#E7A26C"
    },
    "Sân": {
        "dat_hop": "MỀM – TỪ BI – ÍT XUNG ĐỘT",
        "cach_cham": "Mềm lại → quan sát phản ứng → giảm đối kháng.",
        "dao_hanh": "Vô Tưởng Hành",
        "dao_hanh_giai_thich": "Quan sát cảm xúc cho đến khi tự lắng xuống.",
        "loi_khuyen": "Khi bực, dừng lại một nhịp, hạ giọng xuống, chọn cách đáp mềm thay vì thắng–thua.",
        "cau_dat": "MỀM LÀ MẠNH",
        "canh_bao_lech": "Sân cao nhưng điều tiết thấp → dễ phản ứng quá mức.",
        "dinh_huong_1d4": "Chọn môi trường mềm → giảm đối đầu.",
        "icon": "⚡",
        "color": "#D37A74"
    },
    "Si": {
        "dat_hop": "ĐƠN GIẢN – RÕ RÀNG – ÍT LỰA CHỌN",
        "cach_cham": "Đơn giản hóa → giảm lựa chọn → giữ mọi thứ rõ ràng.",
        "dao_hanh": "Hữu Nguyện + Vô Nguyện",
        "dao_hanh_giai_thich": "Làm đều nhưng giảm mong cầu, đi chậm.",
        "loi_khuyen": "Dọn bớt việc và lựa chọn, chỉ giữ những gì thật sự cần để đầu óc sáng và nhẹ.",
        "cau_dat": "ĐƠN GIẢN HOÁ ĐỂ THẤY RÕ",
        "canh_bao_lech": "Si cao + Tuệ thấp → dễ mơ hồ, dễ rối.",
        "dinh_huong_1d4": "Giữ cuộc sống rõ ràng, tối giản.",
        "icon": "🌫️",
        "color": "#A8A8A8"
    },
    "Tín": {
        "dat_hop": "THẦY TỐT – BẠN LÀNH – GẦN CHÁNH PHÁP",
        "cach_cham": "Củng cố niềm tin → chọn người đúng → môi trường đúng.",
        "dao_hanh": "Vô Nguyện Hành",
        "dao_hanh_giai_thich": "Bớt mong cầu, bớt cố gắng, sống đơn giản – less is more.",
        "loi_khuyen": "Chọn vài giá trị cốt lõi, bám vào đó khi mọi thứ đổi thay để không bị cuốn trôi.",
        "cau_dat": "GIỮ VỮNG ĐIỀU ĐÚNG",
        "canh_bao_lech": "Tín cao + Dục/Sân mạnh → dễ theo nhầm người hoặc lung lay.",
        "dinh_huong_1d4": "Chọn người đúng, môi trường đúng.",
        "icon": "🪬",
        "color": "#7BAA82"
    },
    "Niệm": {
        "dat_hop": "CHẬM – TĨNH – ÍT NHIỄU",
        "cach_cham": "Quan sát thân–tâm → sống chậm → tạo khoảng lặng.",
        "dao_hanh": "Vô Tưởng + Vô Nguyện",
        "dao_hanh_giai_thich": "Quan sát cảm xúc mà không phản ứng ngay, sống chậm.",
        "loi_khuyen": "Giảm bớt kích thích và việc thừa để có chỗ cho sự nhận biết trong hiện tại.",
        "cau_dat": "LESS IS MORE",
        "canh_bao_lech": "Niệm cao nhưng Sân/Dục mạnh → dễ tán loạn khi cảm xúc mạnh.",
        "dinh_huong_1d4": "Giảm tốc, sống chậm.",
        "icon": "🌿",
        "color": "#A9C8D9"
    },
    "Tuệ": {
        "dat_hop": "ĐÚNG PHÁP – RÕ LÝ – HỌC ĐÚNG",
        "cach_cham": "Thấy rõ → buông → hành ít nhưng đúng.",
        "dao_hanh": "Vô Nguyện + Vô Tưởng",
        "dao_hanh_giai_thich": "Quan sát rõ, không tạo câu chuyện, làm ít mà đúng.",
        "loi_khuyen": "Dùng hiểu biết để thả lỏng, không để trí phân tích kéo bạn vào vòng xoáy suy nghĩ.",
        "cau_dat": "THẤY RÕ RỒI BUÔNG",
        "canh_bao_lech": "Tuệ cao + Dục/Sân mạnh → dễ dùng lý trí để né cảm xúc.",
        "dinh_huong_1d4": "Buông phân tích → hành ít nhưng chuẩn.",
        "icon": "✨",
        "color": "#EEDC82"
    }
}

QUESTIONS = [
    # ===================== TẦNG GỐC =====================
    {
        "id": 1,
        "layer": "goc",
        "text": "Khi bạn bị từ chối (ví dụ: bị từ chối lời đề nghị, ý tưởng, hoặc mong muốn), trong vài giây đầu tiên, điều gì xảy ra rõ nhất trong bạn?",
        "options": [
            {
                "value": "q1_opt_duc",
                "label": "Muốn chứng minh rằng mình xứng đáng.",
                "temperament": "duc",
            },
            {
                "value": "q1_opt_san",
                "label": "Cảm thấy bực hoặc khó chịu.",
                "temperament": "san",
            },
            {
                "value": "q1_opt_si",
                "label": "Đơ, hơi choáng, không biết phản ứng sao.",
                "temperament": "si",
            },
            {
                "value": "q1_opt_tin",
                "label": "Nghĩ rằng chắc do nhân duyên chưa đến.",
                "temperament": "tin",
            },
            {
                "value": "q1_opt_niem",
                "label": "Cảm nhận rõ lực co hoặc nặng trong thân.",
                "temperament": "niem",
            },
            {
                "value": "q1_opt_tue",
                "label": "Tách bản thân ra và quan sát phản ứng đó.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 2,
        "layer": "goc",
        "text": "Khi bạn thấy người khác đạt được điều mà bạn cũng muốn, phản ứng đầu tiên trong bạn là gì?",
        "options": [
            {
                "value": "q2_opt_duc",
                "label": "Muốn đạt được như họ.",
                "temperament": "duc",
            },
            {
                "value": "q2_opt_san",
                "label": "Khó chịu, có chút so sánh trong đầu.",
                "temperament": "san",
            },
            {
                "value": "q2_opt_si",
                "label": "Thu mình lại, mất tự tin.",
                "temperament": "si",
            },
            {
                "value": "q2_opt_tin",
                "label": "Nghĩ rằng mỗi người có con đường riêng.",
                "temperament": "tin",
            },
            {
                "value": "q2_opt_niem",
                "label": "Nhìn thẳng vào cảm giác ghen tị đang khởi lên.",
                "temperament": "niem",
            },
            {
                "value": "q2_opt_tue",
                "label": "Tò mò về nguyên nhân thành công của họ.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 3,
        "layer": "goc",
        "text": "Khi một việc khá quan trọng không diễn ra như bạn mong muốn, điều tự động xuất hiện đầu tiên là gì?",
        "options": [
            {
                "value": "q3_opt_duc",
                "label": "Tìm ngay thứ gì đó để làm mình dễ chịu hơn.",
                "temperament": "duc",
            },
            {
                "value": "q3_opt_san",
                "label": "Nổi sân nhẹ, bực bội trong đầu.",
                "temperament": "san",
            },
            {
                "value": "q3_opt_si",
                "label": "Lúng túng, trống rỗng trong tích tắc.",
                "temperament": "si",
            },
            {
                "value": "q3_opt_tin",
                "label": "Nghĩ rằng đây là một bài học cần trải qua.",
                "temperament": "tin",
            },
            {
                "value": "q3_opt_niem",
                "label": "Cảm nhận rõ cảm xúc khó chịu đang tràn lên.",
                "temperament": "niem",
            },
            {
                "value": "q3_opt_tue",
                "label": "Tìm hiểu nguyên nhân và cơ chế sai ở đâu.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 4,
        "layer": "goc",
        "text": "Khi bạn bị người khác hiểu lầm, điều bạn muốn làm ngay nhất là gì?",
        "options": [
            {
                "value": "q4_opt_duc",
                "label": "Giải thích lại để họ hiểu đúng về mình.",
                "temperament": "duc",
            },
            {
                "value": "q4_opt_san",
                "label": "Phản ứng mạnh để bảo vệ mình.",
                "temperament": "san",
            },
            {
                "value": "q4_opt_si",
                "label": "Không nói nên lời, hơi tê cứng.",
                "temperament": "si",
            },
            {
                "value": "q4_opt_tin",
                "label": "Nhường, nghĩ rằng rồi mọi chuyện sẽ ổn.",
                "temperament": "tin",
            },
            {
                "value": "q4_opt_niem",
                "label": "Nhìn cảm xúc nóng lên trong thân.",
                "temperament": "niem",
            },
            {
                "value": "q4_opt_tue",
                "label": "Tách phần 'bản ngã bị đụng' khỏi tình huống.",
                "temperament": "tue",
            },
        ],
    },
    # ===================== TẦNG ĐIỀU TIẾT =====================
    {
        "id": 5,
        "layer": "dieu_tiet",
        "text": "Khi bạn đối diện một quyết định quan trọng, bạn thường dựa vào điều gì nhiều nhất?",
        "options": [
            {
                "value": "q5_opt_duc",
                "label": "Cảm giác thích hay không thích.",
                "temperament": "duc",
            },
            {
                "value": "q5_opt_san",
                "label": "Điều giúp mình ít bị sai hoặc thiệt nhất.",
                "temperament": "san",
            },
            {
                "value": "q5_opt_si",
                "label": "Ý kiến của người khác.",
                "temperament": "si",
            },
            {
                "value": "q5_opt_tin",
                "label": "Giá trị hoặc lý tưởng sống mà mình theo đuổi.",
                "temperament": "tin",
            },
            {
                "value": "q5_opt_niem",
                "label": "Trạng thái tâm tĩnh lặng, sáng suốt của mình.",
                "temperament": "niem",
            },
            {
                "value": "q5_opt_tue",
                "label": "Logic nhân–quả và ảnh hưởng dài hạn.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 6,
        "layer": "dieu_tiet",
        "text": "Khi gặp một khó khăn kéo dài, điều gì giúp bạn trụ lại tốt nhất?",
        "options": [
            {
                "value": "q6_opt_duc",
                "label": "Những niềm vui nhỏ giúp tự an ủi bản thân.",
                "temperament": "duc",
            },
            {
                "value": "q6_opt_san",
                "label": "Ý chí gồng lên để vượt qua.",
                "temperament": "san",
            },
            {
                "value": "q6_opt_si",
                "label": "Buông thả hoặc trì hoãn, né tránh.",
                "temperament": "si",
            },
            {
                "value": "q6_opt_tin",
                "label": "Bám vào niềm tin hoặc đạo lý sống của mình.",
                "temperament": "tin",
            },
            {
                "value": "q6_opt_niem",
                "label": "Cảm nhận trọn vẹn khó chịu cho đến khi nó lắng xuống.",
                "temperament": "niem",
            },
            {
                "value": "q6_opt_tue",
                "label": "Hiểu đúng bản chất vấn đề để xử lý cho gốc.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 7,
        "layer": "dieu_tiet",
        "text": "Khi bạn bắt đầu học một điều gì mới, bạn thường thiên về cách học nào?",
        "options": [
            {
                "value": "q7_opt_duc",
                "label": "Học những phần đem lại hứng thú, cảm giác thích.",
                "temperament": "duc",
            },
            {
                "value": "q7_opt_san",
                "label": "Bắt đầu với nhiều áp lực và dễ bực khi gặp phần khó.",
                "temperament": "san",
            },
            {
                "value": "q7_opt_si",
                "label": "Học nhưng không sâu, dễ quên, không nắm rõ.",
                "temperament": "si",
            },
            {
                "value": "q7_opt_tin",
                "label": "Học vì muốn sống đúng với lý tưởng hoặc giá trị nào đó.",
                "temperament": "tin",
            },
            {
                "value": "q7_opt_niem",
                "label": "Học bằng trải nghiệm trực tiếp, quan sát bản thân trong quá trình học.",
                "temperament": "niem",
            },
            {
                "value": "q7_opt_tue",
                "label": "Học bằng cách hiểu nguyên lý và gốc rễ của vấn đề.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 8,
        "layer": "dieu_tiet",
        "text": "Khi có một thay đổi lớn trong đời (công việc, nơi sống, mối quan hệ), bạn thường ứng xử thế nào?",
        "options": [
            {
                "value": "q8_opt_duc",
                "label": "Tìm phần nào đó trong hoàn cảnh mới khiến mình dễ chịu nhất.",
                "temperament": "duc",
            },
            {
                "value": "q8_opt_san",
                "label": "Kháng cự sự thay đổi trong lòng, khó chấp nhận.",
                "temperament": "san",
            },
            {
                "value": "q8_opt_si",
                "label": "Tránh nghĩ đến nó, để mọi thứ trôi đi.",
                "temperament": "si",
            },
            {
                "value": "q8_opt_tin",
                "label": "Nhắc lại những điều mình tin để giữ sự ổn định bên trong.",
                "temperament": "tin",
            },
            {
                "value": "q8_opt_niem",
                "label": "Đi từng bước một, quan sát thân–tâm trong quá trình thay đổi.",
                "temperament": "niem",
            },
            {
                "value": "q8_opt_tue",
                "label": "Xem đây là cơ hội để tái cấu trúc cuộc sống hợp lý hơn.",
                "temperament": "tue",
            },
        ],
    },
    # ===================== TẦNG VÔ THỨC VI TẾ =====================
    {
        "id": 9,
        "layer": "vo_thuc",
        "text": "Khi ai đó xúc phạm bạn khá nặng, trong khoảnh khắc đầu tiên, điều gì xuất hiện rõ nhất?",
        "options": [
            {
                "value": "q9_opt_duc",
                "label": "Muốn phản ứng lại ngay để không bị thua.",
                "temperament": "duc",
            },
            {
                "value": "q9_opt_san",
                "label": "Nóng mặt, khó chịu bùng lên.",
                "temperament": "san",
            },
            {
                "value": "q9_opt_si",
                "label": "Đơ, cứng người, không phản ứng kịp.",
                "temperament": "si",
            },
            {
                "value": "q9_opt_tin",
                "label": "Nghĩ rằng chắc họ đang có vấn đề nào đó.",
                "temperament": "tin",
            },
            {
                "value": "q9_opt_niem",
                "label": "Nhận ra rõ lực co hoặc nóng lên trong ngực/bụng.",
                "temperament": "niem",
            },
            {
                "value": "q9_opt_tue",
                "label": "Nhận ra sự bùng lên đó và quan sát nó từ bên ngoài.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 10,
        "layer": "vo_thuc",
        "text": "Khi một cảm xúc tiêu cực mạnh dâng lên (ví dụ: buồn, giận, tủi), điều gì xuất hiện rõ nhất trong bạn?",
        "options": [
            {
                "value": "q10_opt_duc",
                "label": "Muốn làm gì đó ngay để cảm xúc biến mất.",
                "temperament": "duc",
            },
            {
                "value": "q10_opt_san",
                "label": "Không thích cảm xúc đó và muốn chống lại nó.",
                "temperament": "san",
            },
            {
                "value": "q10_opt_si",
                "label": "Tê liệt, không biết đối diện thế nào.",
                "temperament": "si",
            },
            {
                "value": "q10_opt_tin",
                "label": "Nhớ đến một lời dạy hoặc lý tưởng sống.",
                "temperament": "tin",
            },
            {
                "value": "q10_opt_niem",
                "label": "Cảm nhận trực tiếp cảm xúc đó trong thân.",
                "temperament": "niem",
            },
            {
                "value": "q10_opt_tue",
                "label": "Phân tích vì sao cảm xúc đó xuất hiện.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 11,
        "layer": "vo_thuc",
        "text": "Sau một xung đột căng thẳng, khi tâm bạn bắt đầu yên lại, điều gì còn lại rõ nhất?",
        "options": [
            {
                "value": "q11_opt_duc",
                "label": "Nhu cầu tìm lại cảm giác dễ chịu cho bản thân.",
                "temperament": "duc",
            },
            {
                "value": "q11_opt_san",
                "label": "Dư âm khó chịu, tức tối còn sót lại.",
                "temperament": "san",
            },
            {
                "value": "q11_opt_si",
                "label": "Một cảm giác trống trải, lửng lơ.",
                "temperament": "si",
            },
            {
                "value": "q11_opt_tin",
                "label": "Một suy nghĩ về đạo lý hoặc giá trị sống.",
                "temperament": "tin",
            },
            {
                "value": "q11_opt_niem",
                "label": "Một sự biết lặng lẽ, không lời, chỉ đang biết.",
                "temperament": "niem",
            },
            {
                "value": "q11_opt_tue",
                "label": "Một cái thấy rõ hơn về bản chất của xung đột đó.",
                "temperament": "tue",
            },
        ],
    },
    {
        "id": 12,
        "layer": "vo_thuc",
        "text": "Khi bạn ở một mình trong một căn phòng yên tĩnh, điều gì xuất hiện đầu tiên trong bạn?",
        "options": [
            {
                "value": "q12_opt_duc",
                "label": "Muốn tìm thứ gì đó để giải trí hoặc làm cho vui.",
                "temperament": "duc",
            },
            {
                "value": "q12_opt_san",
                "label": "Có một cảm giác khó chịu nhẹ, không rõ vì sao.",
                "temperament": "san",
            },
            {
                "value": "q12_opt_si",
                "label": "Không biết nên làm gì, hơi lạc hướng.",
                "temperament": "si",
            },
            {
                "value": "q12_opt_tin",
                "label": "Một ý niệm hoặc suy nghĩ về điều mình tin.",
                "temperament": "tin",
            },
            {
                "value": "q12_opt_niem",
                "label": "Cảm nhận sự tĩnh lặng và biết rằng mình đang biết.",
                "temperament": "niem",
            },
            {
                "value": "q12_opt_tue",
                "label": "Một dòng quan sát sắc bén, phân biệt rõ các trạng thái.",
                "temperament": "tue",
            },
        ],
    },
]

TEMPERAMENT_KEYS = ["duc", "san", "si", "tin", "niem", "tue"]
LAYER_KEYS = ["goc", "dieu_tiet", "vo_thuc"]

# ============================================================================
# HÀM XỬ LÝ CSV - ĐÃ BỎ (app không lưu kết quả)
# ============================================================================

# ============================================================================
# HÀM TÍNH ĐIỂM VÀ TÓM TẮT 3 TẦNG
# ============================================================================

def calculate_scores(answers: list[dict]) -> tuple[dict, dict, dict]:
    """
    answers: list các dict dạng:
      {
        "question_id": int,
        "value": str,
        "temperament": str,
        "layer": str,
      }

    Trả về:
      total_scores: dict {temperament: int}
      layer_scores: dict {layer: {temperament: int}}
      summary: dict chứa các kết luận chính
    """
    total_scores = {k: 0 for k in TEMPERAMENT_KEYS}
    layer_scores = {layer: {k: 0 for k in TEMPERAMENT_KEYS} for layer in LAYER_KEYS}

    for ans in answers:
        t = ans["temperament"]
        layer = ans["layer"]
        if t not in total_scores or layer not in layer_scores:
            continue
        total_scores[t] += 1
        layer_scores[layer][t] += 1

    sorted_overall = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    primary_temperament = sorted_overall[0][0] if sorted_overall else None
    secondary_temperament = sorted_overall[1][0] if len(sorted_overall) > 1 else None

    core_group = ["duc", "san", "si"]
    core_scores = {k: layer_scores["goc"][k] for k in core_group}
    core_sorted = sorted(core_scores.items(), key=lambda x: x[1], reverse=True)
    core_main = core_sorted[0][0] if core_sorted and core_sorted[0][1] > 0 else None

    reg_group = ["tin", "niem", "tue"]
    reg_scores = {k: layer_scores["dieu_tiet"][k] for k in reg_group}
    reg_sorted = sorted(reg_scores.items(), key=lambda x: x[1], reverse=True)
    regulator_main = reg_sorted[0][0] if reg_sorted and reg_sorted[0][1] > 0 else None

    deep_scores = {
        "niem": layer_scores["vo_thuc"]["niem"],
        "tue": layer_scores["vo_thuc"]["tue"],
    }
    deep_sorted = sorted(deep_scores.items(), key=lambda x: x[1], reverse=True)
    deep_main = deep_sorted[0][0] if deep_sorted and deep_sorted[0][1] > 0 else None

    # TIE-BREAK: nếu tổng điểm Niệm và Tuệ bằng nhau, ưu tiên tầng vô thức
    if total_scores["niem"] == total_scores["tue"] and deep_main in ["niem", "tue"]:
        primary_temperament = deep_main
        other = "tue" if deep_main == "niem" else "niem"
        if total_scores[other] > 0:
            secondary_temperament = other

    summary = {
        "primary_temperament": primary_temperament,
        "secondary_temperament": secondary_temperament,
        "overall_sorted": sorted_overall,
        "core_main": core_main,
        "core_scores": core_scores,
        "regulator_main": regulator_main,
        "regulator_scores": reg_scores,
        "deep_main": deep_main,
        "deep_scores": deep_scores,
    }

    return total_scores, layer_scores, summary

# ============================================================================
# HÀM TÍNH NGUY CƠ THEO BỘ ĐÔI
# ============================================================================

def get_nguy_co(hat_chinh, hat_phu, total_scores=None):
    """Tự động sinh nguy cơ theo bộ đôi hạt chính + hạt hỗ trợ."""
    if not hat_chinh:
        return None
    
    # Nếu có hạt hỗ trợ, luôn dùng logic pair-based trước
    if hat_phu:
        nguy_co_map = {
            ("Tuệ", "Niệm"): "Dễ phân tích quá mức, xa rời trải nghiệm.",
            ("Tuệ", "Tín"): "Dễ lý tưởng hóa, tin điều sai.",
            ("Niệm", "Tuệ"): "Dễ quan sát nhiều nhưng không xử lý cảm xúc.",
            ("Niệm", "Tín"): "Dễ lệ thuộc vào giá trị/niềm tin cố định.",
            ("Tín", "Tuệ"): "Dễ chấp vào lý tưởng đúng/sai.",
            ("Tín", "Niệm"): "Dễ lệ thuộc vào giá trị/niềm tin cố định.",
        }
        pair = (hat_chinh, hat_phu)
        nguy_co = nguy_co_map.get(pair, None)
        if nguy_co:
            return nguy_co
    
    # Chỉ áp dụng điều kiện đặc biệt khi KHÔNG có hạt hỗ trợ
    if not hat_phu and total_scores:
        niem_score = total_scores.get("niem", 0)
        tin_score = total_scores.get("tin", 0)
        
        # Điều kiện đặc biệt cho Tuệ khi không có hạt hỗ trợ
        if hat_chinh == "Tuệ":
            if niem_score <= 1:
                return "Tuệ mạnh nhưng Niệm thấp → dễ phân tích quá mức, tách khỏi cảm xúc thật."
            if tin_score <= 1:
                return "Tuệ mạnh nhưng Tín thấp → không có điểm tựa giá trị, dễ hoang mang khi nhiều lựa chọn."
    
    return None

# ============================================================================
# HÀM GỌI GPT
# ============================================================================

def calculate_tiers(total_scores, layer_scores, summary):
    """Tự tính 3 tầng không cần GPT."""
    # Chuyển total_scores từ key lowercase (duc, san, si...) sang key Capitalize (Duc, San, Si...)
    scores = {}
    label_map = {
        "duc": "Duc",
        "san": "San",
        "si": "Si",
        "tin": "Tin",
        "niem": "Niem",
        "tue": "Tue",
    }
    label_map_vn = {
        "Duc": "Dục",
        "San": "Sân",
        "Si": "Si",
        "Tin": "Tín",
        "Niem": "Niệm",
        "Tue": "Tuệ",
    }
    
    for key, value in total_scores.items():
        key_cap = label_map.get(key, key.capitalize())
        scores[key_cap] = value
    
    # Thứ tự ưu tiên cho hạt chính: Tuệ > Niệm > Tín > Dục > Sân > Si
    priority_main = ["Tue", "Niem", "Tin", "Duc", "San", "Si"]
    
    # 1. Hạt chính = điểm cao nhất
    max_score = max(scores.values())
    candidates_main = [k for k, v in scores.items() if v == max_score]
    hat_chinh = None
    for p in priority_main:
        if p in candidates_main:
            hat_chinh = p
            break
    
    # 2. Hạt hỗ trợ = CHỈ chọn trong nhóm Tín, Niệm, Tuệ (trừ hạt chính)
    # Loại hoàn toàn Dục, Sân, Si khỏi danh sách ứng viên
    nhom_sang = ["Tin", "Niem", "Tue"]
    # Loại hạt chính khỏi nhóm sáng
    nhom_sang_con_lai = [h for h in nhom_sang if h != hat_chinh]
    
    # Chỉ xét điểm trong nhóm sáng còn lại
    scores_phu = {k: v for k, v in scores.items() if k in nhom_sang_con_lai}
    
    if scores_phu:
        # Tìm điểm cao nhất trong nhóm sáng còn lại
        max_score_phu = max(scores_phu.values())
        candidates_sub = [k for k, v in scores_phu.items() if v == max_score_phu]
        
        # Ưu tiên theo hạt chính
        hat_phu = None
        if hat_chinh == "Tue":
            # Nếu hạt chính = Tuệ: ưu tiên Tín > Niệm
            priority_phu = ["Tin", "Niem"]
        elif hat_chinh == "Tin":
            # Nếu hạt chính = Tín: ưu tiên Tuệ > Niệm
            priority_phu = ["Tue", "Niem"]
        elif hat_chinh == "Niem":
            # Nếu hạt chính = Niệm: ưu tiên Tuệ > Tín
            priority_phu = ["Tue", "Tin"]
        else:
            # Hạt chính là Dục/Sân/Si: ưu tiên mặc định
            priority_phu = ["Tin", "Niem", "Tue"]
        
        for p in priority_phu:
            if p in candidates_sub:
                hat_phu = p
                break
    else:
        hat_phu = None
    
    # Ánh xạ key tiếng Anh → label tiếng Việt
    hat_chinh_label = label_map_vn[hat_chinh] if hat_chinh else None
    hat_phu_label = label_map_vn[hat_phu] if hat_phu else None
    
    # Hạt gốc = max(Dục, Sân, Si)
    goc_scores = layer_scores.get("goc", {})
    duc_score = goc_scores.get("duc", 0)
    san_score = goc_scores.get("san", 0)
    si_score = goc_scores.get("si", 0)
    
    if duc_score > san_score and duc_score > si_score:
        hat_goc = "Dục"
    elif san_score > duc_score and san_score > si_score:
        hat_goc = "Sân"
    elif si_score > duc_score and si_score > san_score:
        hat_goc = "Si"
    else:
        hat_goc = "Không rõ"
    
    # Điều tiết = max(Tín, Niệm, Tuệ)
    dieu_tiet_scores = layer_scores.get("dieu_tiet", {})
    tin_score = dieu_tiet_scores.get("tin", 0)
    niem_score = dieu_tiet_scores.get("niem", 0)
    tue_score = dieu_tiet_scores.get("tue", 0)
    
    if tin_score > niem_score and tin_score > tue_score:
        dieu_tiet = "Tín"
    elif niem_score > tin_score and niem_score > tue_score:
        dieu_tiet = "Niệm"
    elif tue_score > tin_score and tue_score > niem_score:
        dieu_tiet = "Tuệ"
    else:
        dieu_tiet = None
    
    # Vi tế = Niệm hoặc Tuệ (điểm nào cao hơn)
    vo_thuc_scores = layer_scores.get("vo_thuc", {})
    niem_vi_te = vo_thuc_scores.get("niem", 0)
    tue_vi_te = vo_thuc_scores.get("tue", 0)
    
    if niem_vi_te > tue_vi_te:
        vi_te = "Niệm"
    elif tue_vi_te > niem_vi_te:
        vi_te = "Tuệ"
    else:
        vi_te = None
    
    return {
        "can_tanh_chinh": hat_chinh_label,
        "can_tanh_phu": hat_phu_label,
        "tang_goc": hat_goc,
        "tang_dieu_tiet": dieu_tiet,
        "tang_vi_te": vi_te
    }

# ============================================================================
# HÀM HIỂN THỊ KẾT QUẢ
# ============================================================================

def render_results(total_scores, layer_scores, summary, tier_result, mapping_data, user_answers=None, questions=None):
    """Hiển thị kết quả test hạt giống tâm."""
    st.markdown("---")
    st.header("📊 Kết quả")

    # Chỉ hiển thị căn tánh chính & phụ
    can_tanh_chinh_label = tier_result.get("can_tanh_chinh")
    can_tanh_phu_label = tier_result.get("can_tanh_phu")
    
    st.subheader("1. Hạt nổi trội")
    if can_tanh_chinh_label:
        st.markdown(f"**Hạt chính:** {can_tanh_chinh_label}")
    if can_tanh_phu_label:
        st.markdown(f"**Hạt hỗ trợ:** {can_tanh_phu_label}")
    
    # Lấy dữ liệu từ mapping
    if can_tanh_chinh_label and can_tanh_chinh_label in MAPPING:
        map_data = MAPPING[can_tanh_chinh_label]
        
        # Hiển thị icon
        icon_value = map_data.get("icon", "🌱")
        st.markdown(
            f"<div class='trait-icon-wrapper'><div class='trait-icon'>{icon_value}</div></div>",
            unsafe_allow_html=True
        )
        
        st.subheader("2. Mảnh đất phù hợp")
        st.write(f"**{map_data['dat_hop']}**")
        st.write(map_data.get("cach_cham", ""))

        st.subheader("3. Cách chăm phù hợp")
        st.write(f"**{map_data['dao_hanh']}**")
        st.write(map_data.get("dao_hanh_giai_thich", ""))

        st.subheader("4. Tuyên ngôn & Lời khuyên")
        st.markdown(f"**{map_data.get('cau_dat', '—')}**")
        st.write(map_data.get("loi_khuyen", "—"))

        st.subheader("5. Nguy cơ")
        # Tự động sinh nguy cơ theo bộ đôi hạt chính + hạt hỗ trợ
        nguy_co = get_nguy_co(can_tanh_chinh_label, can_tanh_phu_label, total_scores)
        if nguy_co:
            st.write(nguy_co)
        else:
            st.write(map_data.get('canh_bao_lech', '—'))

        st.subheader("6. Định hướng sống")
        st.write(map_data.get("dinh_huong_1d4", "—"))
    else:
        st.warning("Không tìm thấy dữ liệu mapping cho hạt giống tâm này.")

    st.markdown("---")
    
    # Footer với text và nút tải xuống căn giữa
    st.markdown(
        """
        <p style='text-align:center; font-size:0.95rem; line-height:1.5;'>
        Hãy chụp màn hình để lưu kết quả.<br/>
        Hoặc
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # Nút tải xuống file txt
    if user_answers and questions and can_tanh_chinh_label:
        export_full = build_full_export_text(
            questions=questions,
            user_answers=user_answers,
            scores=total_scores,
            main_trait=can_tanh_chinh_label,
            sub_trait=can_tanh_phu_label,
            mapping=MAPPING
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Tải xuống kết quả đầy đủ (.txt)",
                data=export_full,
                file_name="ket_qua_6_hat_tam.txt",
                mime="text/plain",
                use_container_width=True,
            )


# Hàm save_result đã bỏ - app không lưu kết quả

# ============================================================================
# HÀM XUẤT FILE TXT
# ============================================================================

def build_full_export_text(questions, user_answers, scores, main_trait, sub_trait, mapping):
    """Tạo nội dung file txt đầy đủ để tải xuống."""
    lines = []
    lines.append("KẾT QUẢ BÀI TEST 6 HẠT GIỐNG TÂM")
    lines.append("")
    lines.append("=" * 50)
    lines.append("")

    # Phần 1 – 12 câu hỏi & câu trả lời
    lines.append("1. 12 CÂU HỎI & CÂU TRẢ LỜI")
    lines.append("")

    for i in range(len(questions)):
        q_data = user_answers[i]
        question_text = q_data["question_text"]
        choice_label = q_data["choice_label"]
        choice_text = q_data["choice_text"]

        lines.append(f"• Câu {i+1}: {question_text}")
        lines.append(f"  → Bạn chọn: {choice_label}. {choice_text}")
        lines.append("")

    lines.append("=" * 50)
    lines.append("")

    # Phần 2 – Hạt nổi trội
    lines.append("2. HẠT NỔI TRỘI")
    lines.append("")
    lines.append(f"• Hạt chính: {main_trait}")
    if sub_trait:
        lines.append(f"• Hạt hỗ trợ: {sub_trait}")
    lines.append("")
    
    # Debug: Điểm tổng 6 hạt
    lines.append("ĐIỂM TỔNG 6 HẠT:")
    label_map_vn = {
        "duc": "Dục",
        "san": "Sân",
        "si": "Si",
        "tin": "Tín",
        "niem": "Niệm",
        "tue": "Tuệ",
    }
    for k in ["duc", "san", "si", "tin", "niem", "tue"]:
        lines.append(f"- {label_map_vn[k]}: {scores.get(k, 0)}")
    lines.append("")

    trait_info = mapping.get(main_trait, {})

    dat_hop = trait_info.get("dat_hop", "")
    cach_cham = trait_info.get("cach_cham", "")
    dao_hanh = trait_info.get("dao_hanh", "")
    dao_hanh_giai_thich = trait_info.get("dao_hanh_giai_thich", "")
    loi_khuyen = trait_info.get("loi_khuyen", "")
    mantra = trait_info.get("cau_dat", "")
    canh_bao = trait_info.get("canh_bao_lech", "")
    dinh_huong = trait_info.get("dinh_huong_1d4", "")

    # Phần 3 – Mảnh đất phù hợp
    lines.append("3. MẢNH ĐẤT PHÙ HỢP")
    lines.append("")
    lines.append(f"• {dat_hop}")
    lines.append("")

    # Phần 4 – Cách chăm phù hợp
    lines.append("4. CÁCH CHĂM PHÙ HỢP")
    lines.append("")
    lines.append(f"• {cach_cham}")
    lines.append("")

    # Phần 5 – Tuyên ngôn & Lời khuyên
    lines.append("5. TUYÊN NGÔN & LỜI KHUYÊN")
    lines.append("")
    lines.append(f"• Tuyên ngôn: {mantra}")
    lines.append(f"• Lời khuyên: {loi_khuyen}")
    lines.append("")

    # Phần 6 – Nguy cơ
    lines.append("6. NGUY CƠ")
    lines.append("")
    lines.append(f"• {canh_bao}")
    lines.append("")

    # Phần 7 – Định hướng sống
    lines.append("7. ĐỊNH HƯỚNG SỐNG")
    lines.append("")
    lines.append(f"• {dinh_huong}")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# GIAO DIỆN STREAMLIT
# ============================================================================

def main():
    # --- HEADER TITLE ---
    st.markdown(
        """
        <h1 style="
            text-align: center;
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
        ">
            Chỉ cần gieo hạt vào đúng đất, tự nhiên sẽ chăm lo cho bạn.
        </h1>
        """,
        unsafe_allow_html=True
    )
    
    # --- HEADER IMAGE (hat_giong_tam.png) ---
    from PIL import Image
    
    # Kiểm tra đường dẫn ảnh
    img_path = "images/hat_giong_tam.png"
    if not os.path.exists(img_path):
        img_path = "hat_giong_tam.png"  # Thử đường dẫn gốc
    
    if os.path.exists(img_path):
        header_img = Image.open(img_path)
        st.markdown(
            """
            <div style="display:flex; justify-content:center; margin-top: 0.3rem; margin-bottom: 0.3rem;">
                <div style="max-width: 480px; width: 100%;">
            """,
            unsafe_allow_html=True
        )
        st.image(header_img, use_container_width=True)
        st.markdown(
            """
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # --- HEADER SUBTITLE / REMINDER ---
    st.markdown(
        """
        <p style="
            text-align: center;
            font-size: 0.95rem;
            opacity: 0.95;
            margin-top: 0.4rem;
            margin-bottom: 1.2rem;
        ">
            Hãy trả lời bằng phản ứng thật của bạn, vì hạt nào cần đất nấy — thực lòng sẽ cho ra kết quả tốt cho bạn.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Khởi tạo shuffled_options nếu chưa có
    if "shuffled_options" not in st.session_state:
        st.session_state["shuffled_options"] = {}
        for q in QUESTIONS:
            opts = q["options"].copy()
            random.shuffle(opts)
            st.session_state["shuffled_options"][q["id"]] = opts

    temper_map = {
        opt["value"]: (opt["temperament"], q["layer"])
        for q in QUESTIONS
        for opt in q["options"]
    }

    with st.form("quiz_form"):
        answers_dict = {}

        for i, q in enumerate(QUESTIONS, start=1):
            st.markdown(f"**Câu {i}. {q['text']}**")
            opts = st.session_state["shuffled_options"][q["id"]]
            choice = st.radio(
                "",
                options=[opt["value"] for opt in opts],
                format_func=lambda v, opts=opts: next(
                    o["label"] for o in opts if o["value"] == v
                ),
                key=f"q_{q['id']}",
                index=None,
                label_visibility="collapsed",
            )
            answers_dict[q["id"]] = choice
            if i < len(QUESTIONS):
                st.markdown("")

        submitted = st.form_submit_button("Xem kết quả", type="primary")

    if submitted:
        if None in answers_dict.values():
            st.warning("⚠️ Vui lòng trả lời tất cả các câu hỏi.")
        else:
            answers = []
            user_answers = {}  # Lưu câu trả lời để export
            
            for i, q in enumerate(QUESTIONS):
                user_choice_value = answers_dict[q["id"]]
                temper, layer = temper_map[user_choice_value]
                opts = st.session_state["shuffled_options"][q["id"]]
                option_label = next(
                    o["label"] for o in opts if o["value"] == user_choice_value
                )
                
                # Tìm index của option để tạo label (A, B, C, ...)
                option_index = next(
                    idx for idx, opt in enumerate(opts) if opt["value"] == user_choice_value
                )
                choice_label = chr(65 + option_index)  # A, B, C, ...

                answers.append(
                    {
                        "question_id": q["id"],
                        "value": user_choice_value,
                        "temperament": temper,
                        "layer": layer,
                        "question_text": q["text"],
                        "option_label": option_label,
                    }
                )
                
                # Lưu vào user_answers để export
                user_answers[i] = {
                    "question_text": q["text"],
                    "choice_label": choice_label,
                    "choice_text": option_label,
                }

            total_scores, layer_scores, summary = calculate_scores(answers)

            # Tự tính 3 tầng không cần GPT
            tier_result = calculate_tiers(total_scores, layer_scores, summary)

            # Lấy căn tánh chính từ tier_result
            can_tanh_chinh_label = tier_result.get("can_tanh_chinh")
            
            # Lấy dữ liệu từ mapping
            mapping_data = {}
            if can_tanh_chinh_label and can_tanh_chinh_label in MAPPING:
                mapping_data = MAPPING[can_tanh_chinh_label]

            # Khối 2: Kết quả
            st.divider()
            with st.container():
                st.subheader("2. Kết quả")
                render_results(
                    total_scores, 
                    layer_scores, 
                    summary, 
                    tier_result, 
                    mapping_data,
                    user_answers=user_answers,
                    questions=QUESTIONS
                )



if __name__ == "__main__":
    main()
