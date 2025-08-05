import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { KeyValuePipe, TitleCasePipe } from '@angular/common';
import { MatSlideToggleModule } from "@angular/material/slide-toggle";

@Component({
  selector: 'app-detail-card',
  imports: [TitleCasePipe, KeyValuePipe, MatSlideToggleModule],
  templateUrl: './detail-card.component.html',
  styleUrl: './detail-card.component.css'
})
export class DetailCardComponent implements OnChanges {

  @Input() mockImages: any[] = []
  @Input() headerValue: any = undefined

  constructor() { }

  ngOnChanges(changes: SimpleChanges): void {

    this.headerValue = undefined

    setTimeout(() => {
      this.headerValue = changes['headerValue']['currentValue']
    }, 1);
    
  }


  onImageLoad(imgEle: HTMLImageElement, img: any) {

    const renderedWidth = imgEle.clientWidth;   // CSS rendered width
    const renderedHeight = imgEle.clientHeight; // CSS rendered height

    const originalWidth = imgEle.naturalWidth;  // Original image width
    const originalHeight = imgEle.naturalHeight; // Original image height

    let scaleX = renderedWidth / originalWidth;
    let scaleY = renderedHeight / originalHeight;

    img.forEach((obj: any) => {

      const [x1, y1, x2, y2] = obj.box;

      obj.box = [
        x1 * scaleX,
        y1 * scaleY,
        (x2 - x1) * scaleX,
        (y2 - y1) * scaleY
      ]
    })

  }

}
