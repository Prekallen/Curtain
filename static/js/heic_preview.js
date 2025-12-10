// static/js/heic_preview.js

(function($) {
    // 파일 입력 필드 변경 이벤트 핸들러
    $(document).on('change', '.image-input', function(e) {
        const fileInput = e.target;
        const file = fileInput.files[0];
        // .image-form 내부에서 .image-preview를 찾습니다.
        const previewElement = $(this).closest('.image-form').find('.image-preview');

        if (!file) {
            previewElement.hide().attr('src', '');
            return;
        }

        const fileName = file.name.toLowerCase();

        // HEIC/HEIF 파일인지 확인
        if (fileName.endsWith('.heic') || fileName.endsWith('.heif')) {
            // heic2any 라이브러리가 로드되었는지 확인
            if (typeof heic2any === 'undefined') {
                console.error("heic2any 라이브러리가 로드되지 않았습니다.");
                // 로드되지 않았다면 일반 처리로 폴백
                processDefaultImage(file, previewElement);
                return;
            }

            // HEIC/HEIF 파일 처리 로직
            heic2any({
                blob: file,
                toType: 'image/jpeg',
                quality: 0.9,
            })
                .then(function (conversionResult) {
                    // 변환된 Blob을 미리보기 URL로 설정
                    const url = URL.createObjectURL(conversionResult);
                    previewElement.attr('src', url).show();
                })
                .catch(function (error) {
                    console.error("HEIC 변환 오류 (클라이언트):", error);
                    previewElement.hide().attr('src', '');
                    alert('HEIC 파일 미리보기에 실패했습니다.');
                });

        } else if (file.type.startsWith('image/')) {
            // 일반 이미지 파일 처리 로직
            processDefaultImage(file, previewElement);
        } else {
            // 기타 파일
            previewElement.hide().attr('src', '');
        }
    });

    // 일반 이미지 (JPEG, PNG 등) 처리를 위한 헬퍼 함수
    function processDefaultImage(file, previewElement) {
        const reader = new FileReader();
        reader.onload = function(event) {
            previewElement.attr('src', event.target.result).show();
        };
        reader.readAsDataURL(file);
    }

})(jQuery);